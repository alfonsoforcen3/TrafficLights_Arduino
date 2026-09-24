// traffic_light.ino — Traffic Light Indicator for AI CLI Sessions
// Configured for Arduino Uno / Nano / ESP32
//
// Wiring:
//   Pin  9 -> Resistor (220-330Ω) -> Green LED Anode (+)
//   Pin 10 -> Resistor (220-330Ω) -> Yellow LED Anode (+)
//   Pin 11 -> Resistor (220-330Ω) -> Red LED Anode (+)
//   GND   -> All 3 LED Cathodes (-)

const int PIN_GREEN  = 9;   // Digital Pin 9: Green LED (Finished / Ready)
const int PIN_YELLOW = 10;  // Digital Pin 10: Yellow LED (Working / Processing)
const int PIN_RED    = 11;  // Digital Pin 11: Red LED (Needs Input / Blocked)

char currentMode = 'O';
unsigned long lastBlinkTime = 0;
const unsigned long BLINK_INTERVAL = 300; // 300ms on, 300ms off
bool blinkState = false;

void setAll(int redState, int yellowState, int greenState) {
  digitalWrite(PIN_RED, redState);
  digitalWrite(PIN_YELLOW, yellowState);
  digitalWrite(PIN_GREEN, greenState);
}

void setColor(char c) {
  switch (c) {
    case 'R':
    case 'r':
      currentMode = 'R';
      setAll(HIGH, LOW, LOW); // Solid Red
      break;
    case 'B': // Blinking Red for Input Required
    case 'b':
      currentMode = 'B';
      blinkState = true;
      lastBlinkTime = millis();
      setAll(HIGH, LOW, LOW);
      break;
    case 'Y':
    case 'y':
      currentMode = 'Y';
      setAll(LOW, HIGH, LOW); // Solid Yellow
      break;
    case 'G':
    case 'g':
      currentMode = 'G';
      setAll(LOW, LOW, HIGH); // Solid Green
      break;
    case 'O': // Off
    case 'o':
      currentMode = 'O';
      setAll(LOW, LOW, LOW);
      break;
    case 'T': // Test cycle
    case 't':
      runStartupTest();
      break;
    default:
      // Ignore unknown characters
      break;
  }
}

void runStartupTest() {
  setAll(LOW, LOW, LOW);
  delay(150);
  
  digitalWrite(PIN_RED, HIGH);
  delay(250);
  digitalWrite(PIN_RED, LOW);
  
  digitalWrite(PIN_YELLOW, HIGH);
  delay(250);
  digitalWrite(PIN_YELLOW, LOW);
  
  digitalWrite(PIN_GREEN, HIGH);
  delay(250);
  digitalWrite(PIN_GREEN, LOW);
  delay(150);

  // Flash all once
  setAll(HIGH, HIGH, HIGH);
  delay(200);
  setAll(LOW, LOW, LOW);
}

void setup() {
  pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_YELLOW, OUTPUT);
  pinMode(PIN_GREEN, OUTPUT);

  // Run hardware test on boot
  runStartupTest();

  // Initialize Serial
  Serial.begin(115200);
  Serial.println(F("TRAFFIC_LIGHT_READY"));
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    setColor(c);
  }

  // Handle non-blocking blinking if in 'B' mode
  if (currentMode == 'B') {
    unsigned long now = millis();
    if (now - lastBlinkTime >= BLINK_INTERVAL) {
      lastBlinkTime = now;
      blinkState = !blinkState;
      digitalWrite(PIN_RED, blinkState ? HIGH : LOW);
    }
  }
}
