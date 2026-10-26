// Cable-only ESP32-C3 LED diagnostic. No Wi-Fi/Bluetooth/provider integration.
// Owner wiring: red GPIO3, amber GPIO2, green GPIO1; active-high outputs.
#include <Arduino.h>
#if !CONFIG_IDF_TARGET_ESP32C3
#error "Select the identified ESP32-C3 target, not an nRF or another ESP family."
#endif
constexpr uint8_t RED = 3, AMBER = 2, GREEN = 1;
void lights(bool red, bool amber, bool green, const char* phase) {
  digitalWrite(RED, red ? HIGH : LOW);
  digitalWrite(AMBER, amber ? HIGH : LOW);
  digitalWrite(GREEN, green ? HIGH : LOW);
  Serial.printf("{\"firmware\":\"clawdy-esp32c3-led-test-v1\",\"phase\":\"%s\",\"red_pin\":3,\"amber_pin\":2,\"green_pin\":1,\"GPIO3\":%s,\"GPIO2\":%s,\"GPIO1\":%s}\n",
                phase, digitalRead(RED) ? "true" : "false",
                digitalRead(AMBER) ? "true" : "false", digitalRead(GREEN) ? "true" : "false");
}
void setup() {
  for (uint8_t pin : {RED, AMBER, GREEN}) { digitalWrite(pin, LOW); pinMode(pin, OUTPUT); }
  Serial.begin(115200);
}
void loop() {
  lights(true, false, false, "red"); delay(1400);
  lights(false, true, false, "amber"); delay(1400);
  lights(false, false, true, "green"); delay(1400);
  for (int index = 0; index < 3; ++index) {
    lights(true, true, true, "all-on"); delay(650);
    lights(false, false, false, "all-off"); delay(650);
  }
}
