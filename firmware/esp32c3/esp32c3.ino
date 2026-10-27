// ESP32-C3 factory firmware; actual GPIO definitions must be supplied by factory.
#include <Arduino.h>
#include <ArduinoJson.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <Preferences.h>
#include <driver/gpio.h>
#include <esp_mac.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#if defined(CONFIG_NIMBLE_ENABLED)
#include <services/gap/ble_svc_gap.h>
#elif defined(CONFIG_BLUEDROID_ENABLED)
#include <esp_gap_ble_api.h>
#include <BLE2902.h>
#else
#error "An Arduino-ESP32 BLE backend is required"
#endif
#include "factory_config.h"
#include "runtime.h"
#if !CONFIG_IDF_TARGET_ESP32C3
#error "This firmware targets ESP32-C3 only"
#endif
#if !ARDUINO_USB_CDC_ON_BOOT
#error "Factory USB identity requires CDCOnBoot=cdc"
#endif

static constexpr char SERVICE[] = "6e400001-b5a3-f393-e0a9-e50e24dcca9e";
static constexpr char UART_RX_UUID[] = "6e400002-b5a3-f393-e0a9-e50e24dcca9e";
static constexpr char UART_TX_UUID[] = "6e400003-b5a3-f393-e0a9-e50e24dcca9e";
struct Packet { uint32_t epoch; uint16_t size; uint8_t data[244]; };
QueueHandle_t incoming;
portMUX_TYPE transportMux = portMUX_INITIALIZER_UNLOCKED;
clawdy::PeerState peer;
clawdy::Display display;
clawdy::Transmit usbOutput, bleOutput;
clawdy::OutputProgress usbProgress;
clawdy::Protocol bleParser, usbParser;
uint32_t seenEpoch = 0, lastNotify = 0, lastAdvertise = 0;
bool storageReady = false, advertiseNeeded = true, bleReady = false;
BLEServer* server;
BLECharacteristic* tx;
Preferences names;
String deviceId, bleName;
const char* phase = "searching";
const char* bleError = nullptr;
const char* usbError = nullptr;
bool usbNeedsBoundary = false;

clawdy::PeerSnapshot connection() {
  portENTER_CRITICAL(&transportMux); auto state = peer.snapshot(); portEXIT_CRITICAL(&transportMux); return state;
}
bool currentPeer(uint32_t epoch, uint16_t id) {
  portENTER_CRITICAL(&transportMux); bool ok = peer.accepts(epoch, id); portEXIT_CRITICAL(&transportMux); return ok;
}
void synchronizeConnection() {
  auto state = connection();
  if (state.epoch == seenEpoch) return;
  seenEpoch = state.epoch; bleParser.reset(); bleOutput.reset(); display.peer_changed(state.connected, state.connected_at);
  if (!state.connected) advertiseNeeded = true;
}
void animate() {
  auto frame = display.frame(millis()); phase = frame.phase;
  unsigned duty = frame.green ? CLAWDY_GREEN_DUTY : 0;
  ledcWrite(CLAWDY_GREEN_GPIO, CLAWDY_ACTIVE_HIGH ? duty : CLAWDY_GREEN_PWM_MAX - duty);
  digitalWrite(CLAWDY_AMBER_GPIO, frame.amber == bool(CLAWDY_ACTIVE_HIGH) ? HIGH : LOW);
  digitalWrite(CLAWDY_RED_GPIO, frame.red == bool(CLAWDY_ACTIVE_HIGH) ? HIGH : LOW);
}

void emit(JsonDocument& document, bool bluetooth, bool acknowledgement = false) {
  char encoded[clawdy::Transmit::capacity];
  size_t prefix = !bluetooth && usbNeedsBoundary ? 1 : 0;
  size_t size = measureJson(document);
  if (size + prefix + 1 > sizeof(encoded)) return;
  if (prefix) encoded[0] = '\n';
  serializeJson(document, encoded + prefix, sizeof(encoded) - prefix); size += prefix; encoded[size++] = '\n';
  if ((bluetooth ? bleOutput : usbOutput).enqueue(encoded, size, acknowledgement) && !bluetooth)
    usbNeedsBoundary = false;
}
void flushOutput() {
  // Send only a currently available USB chunk; an unplugged host cannot hold LEDs.
  int available = Serial.availableForWrite();
  size_t written = 0;
  if (available > 0 && usbOutput.remaining()) {
    size_t amount = min(size_t(64), min(size_t(available), usbOutput.remaining()));
    written = Serial.write(usbOutput.data(), amount); usbOutput.advance(written);
  }
  if (usbProgress.stalled(millis(), usbOutput.remaining() != 0, written)) {
    // A vanished/unresponsive USB reader must not retain the ACK input gate.
    // A later Q exposes the persisted name and this delivery failure; its leading
    // newline lets a reader discard the incomplete frame before parsing again.
    usbOutput.reset(); usbParser.reset(); usbNeedsBoundary = true; usbError = "output_stalled";
  }
  auto state = connection();
  if (!state.connected || state.epoch != seenEpoch || state.overflow) { bleOutput.reset(); return; }
  if (bleOutput.remaining() && uint32_t(millis() - lastNotify) >= 5) {
    size_t amount = min(size_t(20), bleOutput.remaining());
    tx->setValue(bleOutput.data(), amount); tx->notify(); bleOutput.advance(amount); lastNotify = millis();
  }
}
bool advertising() {
  if (!bleReady) return false;
#if defined(CONFIG_NIMBLE_ENABLED)
  return BLEDevice::getAdvertising()->isAdvertising();
#else
  return !connection().connected && !advertiseNeeded;
#endif
}
void report(bool bluetooth) {
  synchronizeConnection();
  animate(); auto state = connection();
  JsonDocument data;
  data["firmware"] = "traffic-esp32c3-v1"; data["hardware_family"] = "esp32c3";
  data["transport"] = bluetooth ? "ble" : "usb";
  data["device_id"] = deviceId; data["ble_name"] = bleName;
  data["identity_protocol"] = 1; data["rename_supported"] = storageReady;
  data["ble_connected"] = state.connected; data["advertising"] = advertising();
  data["mode"] = String(display.mode()); data["display_phase"] = phase;
  String green = "GPIO" + String(CLAWDY_GREEN_GPIO), amber = "GPIO" + String(CLAWDY_AMBER_GPIO), red = "GPIO" + String(CLAWDY_RED_GPIO);
  data["green_pin"] = green; data["amber_pin"] = amber; data["red_pin"] = red;
  unsigned applied = ledcRead(CLAWDY_GREEN_GPIO);
  data[green] = CLAWDY_ACTIVE_HIGH ? applied > 0 : applied < CLAWDY_GREEN_PWM_MAX;
  data[amber] = digitalRead(CLAWDY_AMBER_GPIO) == (CLAWDY_ACTIVE_HIGH ? HIGH : LOW);
  data[red] = digitalRead(CLAWDY_RED_GPIO) == (CLAWDY_ACTIVE_HIGH ? HIGH : LOW);
  data["green_pwm_duty"] = CLAWDY_GREEN_DUTY;
  data["green_pwm_applied_duty"] = applied;
  data["green_pwm_resolution_bits"] = CLAWDY_GREEN_PWM_BITS;
  data["green_pwm_frequency"] = ledcReadFreq(CLAWDY_GREEN_GPIO);
  data["green_pwm_target_frequency"] = CLAWDY_GREEN_PWM_HZ;
  if (state.connected && bleParser.count >= 0) data["session_count"] = bleParser.count;
  else data["session_count"] = nullptr;
  data["session_count_kind"] = "working";
  data["working_provider_mask"] = state.connected ? bleParser.provider_mask : 0;
  data["ble_error"] = bleError;
  data["usb_error"] = usbError;
  emit(data, bluetooth);
}

class PersistentName : public clawdy::NameStore {
 public:
  size_t read(char* destination, size_t capacity) override {
    String value = names.getString("ble_name", "");
    if (value.length() >= capacity) return capacity + 1;
    memcpy(destination, value.c_str(), value.length() + 1); return value.length();
  }
  size_t write(const char* value) override { return names.putString("ble_name", value); }
} nameStore;
bool exact(JsonVariantConst value, const char* expected, size_t size) {
  if (!value.is<const char*>()) return false;
  JsonString text = value.as<JsonString>();
  return text.size() == size && memcmp(text.c_str(), expected, size) == 0;
}
void renameUnit(const char* payload, bool bluetooth) {
  JsonDocument request, ack;
  ack["identity_ack"] = "rename"; ack["ok"] = false; ack["persistent"] = false; ack["device_id"] = deviceId;
  const char* error = nullptr;
  auto result = deserializeJson(request, payload, DeserializationOption::NestingLimit(2));
  if (result || !request.is<JsonObject>() || request.size() != 3) error = "Invalid identity JSON";
  else if (!exact(request["op"], "rename", 6) || !exact(request["device_id"], deviceId.c_str(), deviceId.length()))
    error = "Selected device identity does not match";
  else if (!request["name"].is<const char*>()) error = "Name must be a string";
  else if (!storageReady) error = "Persistent rename unavailable";
  else {
    JsonString name = request["name"].as<JsonString>();
    if (!clawdy::valid_name(name.c_str(), name.size())) error = "Name requires 1-29 UTF-8 bytes without controls";
    else if (!clawdy::persist_name(nameStore, name.c_str(), name.size())) error = "Persistent rename write/readback failed";
    else { bleName = String(name.c_str()); ack["ok"] = true; ack["persistent"] = true; }
  }
  ack["ble_name"] = bleName; if (error) ack["error"] = error;
  emit(ack, bluetooth, true);
  // Keep the current BLE connection intact for the ACK; next advertisement/boot
  // applies the persisted name. USB rename while searching refreshes advertising.
  if (!connection().connected && !error) advertiseNeeded = true;
}
void processByte(clawdy::Protocol& parser, uint8_t byte, bool bluetooth) {
  auto event = parser.feed(byte);
  if (event == clawdy::Protocol::Event::Identity) renameUnit(parser.frame, bluetooth);
  else if (event == clawdy::Protocol::Event::Command) {
    if (parser.command == 'X' && !bluetooth) { ESP.restart(); return; }
    if (strchr("GYRBOT", parser.command)) { display.command(parser.command, !bluetooth, millis()); report(bluetooth); }
    else if (parser.command == 'Q') report(bluetooth);
  }
}

class ConnectionCallbacks : public BLEServerCallbacks {
  void accept(BLEServer* source, uint16_t id) {
    portENTER_CRITICAL(&transportMux); bool accepted = peer.connect(id, millis()); portEXIT_CRITICAL(&transportMux);
    if (!accepted) source->disconnect(id);
  }
  void lost(uint16_t id) { portENTER_CRITICAL(&transportMux); peer.disconnect(id); portEXIT_CRITICAL(&transportMux); }
#if defined(CONFIG_NIMBLE_ENABLED)
  void onConnect(BLEServer* source, ble_gap_conn_desc* desc) override { accept(source, desc->conn_handle); }
  void onDisconnect(BLEServer*, ble_gap_conn_desc* desc) override { lost(desc->conn_handle); }
#else
  void onConnect(BLEServer* source, esp_ble_gatts_cb_param_t* param) override { accept(source, param->connect.conn_id); }
  void onDisconnect(BLEServer*, esp_ble_gatts_cb_param_t* param) override { lost(param->disconnect.conn_id); }
#endif
};
class ReceiveCallbacks : public BLECharacteristicCallbacks {
  void receive(BLECharacteristic* characteristic, uint16_t id) {
    auto state = connection(); if (!currentPeer(state.epoch, id)) return;
    auto value = characteristic->getValue(); Packet packet; packet.epoch = state.epoch;
    if (value.length() <= sizeof(packet.data)) {
      packet.size = value.length(); memcpy(packet.data, value.c_str(), packet.size);
      if (xQueueSend(incoming, &packet, 0) == pdTRUE) return;
    }
    portENTER_CRITICAL(&transportMux); peer.overflow(state.epoch); portEXIT_CRITICAL(&transportMux);
  }
#if defined(CONFIG_NIMBLE_ENABLED)
  void onWrite(BLECharacteristic* characteristic, ble_gap_conn_desc* desc) override { receive(characteristic, desc->conn_handle); }
#else
  void onWrite(BLECharacteristic* characteristic, esp_ble_gatts_cb_param_t* param) override { receive(characteristic, param->write.conn_id); }
#endif
};

void advertise() {
  if (!bleReady || connection().connected) return;
  auto ads = BLEDevice::getAdvertising(); ads->stop();
  ads->setScanResponse(true);
#if defined(CONFIG_NIMBLE_ENABLED)
  bool named = ble_svc_gap_device_name_set(bleName.c_str()) == 0;
#else
  bool named = esp_ble_gap_set_device_name(bleName.c_str()) == ESP_OK;
#endif
  BLEAdvertisementData primary, scan;
  primary.setFlags(0x06); primary.setCompleteServices(BLEUUID(SERVICE)); scan.setName(bleName.c_str());
  bool ok = named && ads->setAdvertisementData(primary) && ads->setScanResponseData(scan) && ads->start();
  bleError = ok ? nullptr : "advertising_start_failed"; advertiseNeeded = !ok; lastAdvertise = millis();
}
void setup() {
  Serial.begin(115200); Serial.setTxTimeoutMs(0);
  for (int pin : {CLAWDY_GREEN_GPIO, CLAWDY_AMBER_GPIO, CLAWDY_RED_GPIO}) {
    if (!GPIO_IS_VALID_OUTPUT_GPIO(pin)) { while (true) delay(1000); }
    digitalWrite(pin, CLAWDY_ACTIVE_HIGH ? LOW : HIGH); pinMode(pin, OUTPUT);
  }
  if (!ledcAttach(CLAWDY_GREEN_GPIO, CLAWDY_GREEN_PWM_HZ, CLAWDY_GREEN_PWM_BITS)) { while (true) delay(1000); }
  ledcWrite(CLAWDY_GREEN_GPIO, CLAWDY_ACTIVE_HIGH ? 0 : CLAWDY_GREEN_PWM_MAX);
  uint8_t mac[6]; if (esp_efuse_mac_get_default(mac) != ESP_OK) { while (true) delay(1000); }
  char uid[13], defaultName[20]; clawdy::identity(mac, uid, defaultName); deviceId = uid; bleName = defaultName;
  storageReady = names.begin("clawdy", false);
  if (storageReady) { char stored[30] = {}; size_t size = nameStore.read(stored, sizeof(stored));
    if (size <= 29 && clawdy::valid_name(stored, size)) bleName = stored; }
  incoming = xQueueCreate(16, sizeof(Packet)); if (!incoming) { while (true) delay(1000); }
  BLEDevice::init(bleName.c_str());
  bleReady = BLEDevice::getInitialized();
  if (!bleReady) { bleError = "ble_init_failed"; return; }
  server = BLEDevice::createServer(); server->advertiseOnDisconnect(false); server->setCallbacks(new ConnectionCallbacks());
  auto service = server->createService(SERVICE);
  tx = service->createCharacteristic(UART_TX_UUID, BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_READ);
#if defined(CONFIG_BLUEDROID_ENABLED)
  tx->addDescriptor(new BLE2902()); // NimBLE creates its CCCD from PROPERTY_NOTIFY.
#endif
  auto rx = service->createCharacteristic(UART_RX_UUID, BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR);
  rx->setCallbacks(new ReceiveCallbacks()); service->start(); advertise();
}
void loop() {
  synchronizeConnection();
  auto state = connection();
  if (state.overflow) {
    portENTER_CRITICAL(&transportMux); bool disconnect = peer.request_disconnect(state.epoch); portEXIT_CRITICAL(&transportMux);
    if (disconnect) server->disconnect(state.connection);
  }
  // Bounded receive work. Epoch tags discard old input without deleting the
  // first Q already queued by a freshly connected host.
  Packet packet;
  for (unsigned batch = 0; batch < 16 && !bleOutput.pending_ack() && xQueueReceive(incoming, &packet, 0) == pdTRUE; ++batch) {
    synchronizeConnection(); state = connection();
    if (!currentPeer(packet.epoch, state.connection) || packet.epoch != seenEpoch) continue;
    for (unsigned i = 0; i < packet.size && currentPeer(packet.epoch, state.connection); ++i)
      processByte(bleParser, packet.data[i], true);
  }
  for (unsigned count = 0; count < 64 && Serial.available() && !usbOutput.pending_ack(); ++count)
    processByte(usbParser, Serial.read(), false);
  animate(); flushOutput();
  state = connection();
  if (state.connected && advertising()) BLEDevice::getAdvertising()->stop();
  if (!state.connected && advertiseNeeded && clawdy::advertisement_output_drained(usbOutput, bleOutput)
      && uint32_t(millis() - lastAdvertise) >= 1000) advertise();
  delay(2);
}
