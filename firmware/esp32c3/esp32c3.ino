// PRIVATE engineering candidate. Factory GPIO definitions are deliberately required.
// NUS arrangement follows Espressif's Arduino-ESP32 BLE UART example; original
// implementation below uses its public BLE APIs, not the example's logging loop.
#include <Arduino.h>
#include <ArduinoJson.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <Preferences.h>
#include <driver/gpio.h>
#include <esp_mac.h>
#include <esp_gap_ble_api.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include "factory_config.h"
#include "protocol.h"
#if !CONFIG_IDF_TARGET_ESP32C3
#error "This candidate targets ESP32-C3 only"
#endif
#if !CONFIG_BLUEDROID_ENABLED
#error "This candidate requires the Arduino-ESP32 Bluedroid BLE configuration"
#endif

static constexpr char SERVICE[] = "6e400001-b5a3-f393-e0a9-e50e24dcca9e";
static constexpr char RX[] = "6e400002-b5a3-f393-e0a9-e50e24dcca9e";
static constexpr char TX[] = "6e400003-b5a3-f393-e0a9-e50e24dcca9e";
struct Packet { uint16_t size; uint8_t data[244]; };
QueueHandle_t incoming;
volatile bool connected = false;
volatile bool receiveOverflow = false;
bool wasConnected = false, storageReady = false;
BLEServer* server;
BLECharacteristic* tx;
Preferences names;
clawdy::Protocol bleParser, usbParser;
String deviceId, bleName;
char mode = 'O';
bool greenOn = false, amberOn = false, redOn = false;
const char* phase = "searching";
uint32_t connectedAt = 0, blinkAt = 0, testAt = 0;
bool blinkOn = true, testActive = false;
clawdy::ReceiveRecovery receiveRecovery;

void setLights(bool green, bool amber, bool red) {
  greenOn = green; amberOn = amber; redOn = red;
  unsigned duty = green ? CLAWDY_GREEN_DUTY : 0;
  ledcWrite(CLAWDY_GREEN_GPIO, CLAWDY_ACTIVE_HIGH ? duty : CLAWDY_GREEN_PWM_MAX - duty);
  digitalWrite(CLAWDY_AMBER_GPIO, amber == bool(CLAWDY_ACTIVE_HIGH) ? HIGH : LOW);
  digitalWrite(CLAWDY_RED_GPIO, red == bool(CLAWDY_ACTIVE_HIGH) ? HIGH : LOW);
}

void animate() {
  uint32_t now = millis();
  if (!connected) {
    phase = "searching";
    bool on = (now / 400) % 2 == 0;
    setLights(on, on, on);
  } else if (uint32_t(now - connectedAt) < 960) {
    phase = "connected_show";
    unsigned step = ((now - connectedAt) / 160) % 3;
    setLights(step == 2, step == 1, step == 0);
  } else {
    phase = "tracking";
    if (mode == 'B' && uint32_t(now - blinkAt) >= 300) { blinkAt = now; blinkOn = !blinkOn; }
    if (testActive && uint32_t(now - testAt) < 1500) {
      unsigned step = (now - testAt) / 500;
      setLights(step == 2, step == 1, step == 0);
    } else {
      testActive = false;
      setLights(mode == 'G', mode == 'Y', mode == 'R' || (mode == 'B' && blinkOn));
    }
  }
}

void emit(JsonDocument& document, bool bluetooth) {
  String encoded;
  serializeJson(document, encoded);
  encoded += '\n';
  if (!bluetooth) { Serial.print(encoded); return; }
  // Compatible with the minimum ATT MTU, without requiring a host MTU upgrade.
  for (size_t offset = 0; connected && !receiveOverflow && offset < encoded.length(); offset += 20) {
    size_t size = min(size_t(20), encoded.length() - offset);
    tx->setValue(reinterpret_cast<const uint8_t*>(encoded.c_str() + offset), size);
    tx->notify();
    delay(5);
  }
}

void report(bool bluetooth) {
  animate();
  JsonDocument data;
  data["firmware"] = "traffic-esp32c3-v1";
  data["hardware_family"] = "esp32c3";
  data["transport"] = bluetooth ? "ble" : "usb";
  data["device_id"] = deviceId;
  data["ble_name"] = bleName;
  data["identity_protocol"] = 1;
  data["rename_supported"] = storageReady;
  data["mode"] = String(mode);
  data["display_phase"] = phase;
  String green = "GPIO" + String(CLAWDY_GREEN_GPIO);
  String amber = "GPIO" + String(CLAWDY_AMBER_GPIO);
  String red = "GPIO" + String(CLAWDY_RED_GPIO);
  data["green_pin"] = green; data["amber_pin"] = amber; data["red_pin"] = red;
  data[green] = greenOn; data[amber] = amberOn; data[red] = redOn;
  data["green_pwm_duty"] = CLAWDY_GREEN_DUTY;
  data["green_pwm_resolution_bits"] = CLAWDY_GREEN_PWM_BITS;
  data["green_pwm_frequency"] = CLAWDY_GREEN_PWM_HZ;
  if (bleParser.count >= 0) data["session_count"] = bleParser.count;
  else data["session_count"] = nullptr;
  data["session_count_kind"] = "working";
  data["working_provider_mask"] = bleParser.provider_mask;
  data["battery_supported"] = false;
  emit(data, bluetooth);
}

void renameUnit(const char* payload, bool bluetooth) {
  JsonDocument request, ack;
  ack["identity_ack"] = "rename"; ack["ok"] = false; ack["persistent"] = false;
  ack["device_id"] = deviceId;
  const char* error = nullptr;
  auto result = deserializeJson(request, payload, DeserializationOption::NestingLimit(2));
  if (result || !request.is<JsonObject>()) error = "Invalid identity JSON";
  else if (!request["op"].is<const char*>() || request["op"].as<String>() != "rename" ||
           !request["device_id"].is<const char*>() || request["device_id"].as<String>() != deviceId)
    error = "Selected device identity does not match";
  else if (!request["name"].is<const char*>()) error = "Name must be a string";
  else if (!storageReady) error = "Persistent rename unavailable";
  else {
    JsonString name = request["name"].as<JsonString>();
    if (!clawdy::valid_name(name.c_str(), name.size())) error = "Name requires 1-29 UTF-8 bytes without controls";
    else {
      String next(name.c_str());
      if (names.putString("ble_name", next) != next.length() || names.getString("ble_name", "") != next)
        error = "Persistent rename write/readback failed";
      else {
        bleName = next;
        ack["ok"] = true; ack["persistent"] = true;
      }
    }
  }
  ack["ble_name"] = bleName;
  if (error) ack["error"] = error;
  emit(ack, bluetooth);
  // Keep this connection intact so the host receives its acknowledgement.
  // The next advertising restart applies bleName; no GPIO/profile rewrite.
}

void processByte(clawdy::Protocol& parser, uint8_t byte, bool bluetooth) {
  auto event = parser.feed(byte);
  if (event == clawdy::Protocol::Event::Identity) renameUnit(parser.frame, bluetooth);
  else if (event == clawdy::Protocol::Event::Command) {
    char command = parser.command;
    if (command == 'X' && !bluetooth) { ESP.restart(); return; }
    if (strchr("GYRBO", command)) {
      testActive = false;
      if (mode != command) { mode = command; blinkAt = millis(); blinkOn = true; }
      report(bluetooth);
    } else if (command == 'Q' || command == 'V') report(bluetooth);
    else if (command == 'T') { testActive = true; testAt = millis(); report(bluetooth); }
  }
}

class ConnectionCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer*) override { connected = true; }
  void onDisconnect(BLEServer*) override { connected = false; }
};
class ReceiveCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic* characteristic) override {
    if (receiveOverflow) return;
    auto value = characteristic->getValue();
    Packet packet;
    if (value.length() > sizeof(packet.data)) { receiveOverflow = true; return; }
    packet.size = value.length();
    memcpy(packet.data, value.c_str(), packet.size);
    if (xQueueSend(incoming, &packet, 0) != pdTRUE) receiveOverflow = true;
  }
};

void advertise() {
  esp_ble_gap_set_device_name(bleName.c_str());
  BLEAdvertisementData primary, scan;
  primary.setFlags(0x06);
  primary.setCompleteServices(BLEUUID(SERVICE));
  scan.setName(bleName.c_str());
  auto advertising = server->getAdvertising();
  advertising->setAdvertisementData(primary);
  advertising->setScanResponseData(scan);
  advertising->start();
}

void setup() {
  Serial.begin(115200);
  for (int pin : {CLAWDY_GREEN_GPIO, CLAWDY_AMBER_GPIO, CLAWDY_RED_GPIO}) {
    if (!GPIO_IS_VALID_OUTPUT_GPIO(pin)) { Serial.println("Invalid factory output GPIO"); while (true) delay(1000); }
    digitalWrite(pin, CLAWDY_ACTIVE_HIGH ? LOW : HIGH); pinMode(pin, OUTPUT);
  }
  if (!ledcAttach(CLAWDY_GREEN_GPIO, CLAWDY_GREEN_PWM_HZ, CLAWDY_GREEN_PWM_BITS)) {
    Serial.println("Green PWM setup failed"); while (true) delay(1000);
  }
  setLights(false, false, false);
  uint8_t mac[6];
  if (esp_efuse_mac_get_default(mac) != ESP_OK) { while (true) delay(1000); }
  char uid[13];
  snprintf(uid, sizeof(uid), "%02X%02X%02X%02X%02X%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  deviceId = uid; bleName = "Clawdy-" + deviceId;
  storageReady = names.begin("clawdy", false);
  if (storageReady) {
    String stored = names.getString("ble_name", "");
    if (clawdy::valid_name(stored.c_str(), stored.length())) bleName = stored;
  }
  incoming = xQueueCreate(16, sizeof(Packet));
  if (!incoming) { while (true) delay(1000); }
  BLEDevice::init(bleName.c_str());
  server = BLEDevice::createServer(); server->setCallbacks(new ConnectionCallbacks());
  auto service = server->createService(SERVICE);
  tx = service->createCharacteristic(TX, BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_READ);
  tx->addDescriptor(new BLE2902());
  auto rx = service->createCharacteristic(RX, BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR);
  rx->setCallbacks(new ReceiveCallbacks()); service->start(); advertise();
}

void loop() {
  if (receiveOverflow) {
    receiveRecovery.overflow();
    if (receiveRecovery.take_disconnect_request(connected)) {
      server->disconnect(server->getConnId());
    }
  }
  if (!connected && (wasConnected || !receiveRecovery.accepts_input())) {
    // Only release the overflow latch after the peer is gone. Clear old input
    // before advertising, preserving the first Q queued by the next connection.
    wasConnected = false;
    xQueueReset(incoming);
    bleParser.reset();
    receiveOverflow = false;
    receiveRecovery.released();
    mode = 'O'; testActive = false; advertise();
  } else if (connected && !wasConnected) {
    wasConnected = true;
    bleParser.reset();
    connectedAt = millis();
  }
  Packet packet;
  while (connected && receiveRecovery.accepts_input() && !receiveOverflow &&
         xQueueReceive(incoming, &packet, 0) == pdTRUE) {
    for (unsigned i = 0; i < packet.size && connected && !receiveOverflow; ++i) {
      processByte(bleParser, packet.data[i], true);
    }
  }
  while (Serial.available()) processByte(usbParser, Serial.read(), false);
  animate();
  delay(2);
}
