# Arduino Traffic Light for AI CLI Sessions 🚦

Physical USB traffic light indicator for **Gemini CLI** (and Claude Code), showing your session status at a glance.

| Light | Meaning | Trigger Event (Gemini CLI) |
| :--- | :--- | :--- |
| 🚨 **Blinking Red** | **User Input Required / Prompt / Permission** | Interactive Question / Confirmation |
| 🔴 **Solid Red** | Error / Blocked | Failed Tool / Exception |
| 🟡 **Solid Yellow** | AI working / Thinking / Executing tools | `BeforeAgent` / `PreInvocation` |
| 🟢 **Solid Green** | Turn finished / Ready / Standby | `AfterAgent` / `PostInvocation` / `Stop` |
| ⚫ **Off** | Session closed | `SessionEnd` |

---

## 📌 Hardware Pinout

Configured specifically for your hardware setup:

| LED Color | Arduino Digital Pin | Resistor | Connection |
| :--- | :---: | :---: | :--- |
| 🟢 **Green** | **Pin 9** | 220–330 Ω | Digital Pin 9 ➔ Resistor ➔ Green LED Anode (+) |
| 🟡 **Yellow** | **Pin 10** | 220–330 Ω | Digital Pin 10 ➔ Resistor ➔ Yellow LED Anode (+) |
| 🔴 **Red** | **Pin 11** | 220–330 Ω | Digital Pin 11 ➔ Resistor ➔ Red LED Anode (+) |
| **GND** | **GND** | — | Shared GND Rail ➔ All 3 LED Cathodes (-) |

---

## 🚀 Quick Start

### 1. Flash the Arduino Firmware
1. Open the [traffic_light.ino](firmware/traffic_light/traffic_light.ino) sketch in **Arduino IDE**.
2. Select your board (e.g., *Arduino Uno* or *Arduino Nano*) and Port (`/dev/cu.usbserial-1120`).
3. Click **Upload**.
4. When uploaded, the Arduino will run an automatic startup test sequence (Red ➔ Yellow ➔ Green ➔ Flash) to verify all LEDs.

### 2. Test the Hardware
Run the interactive hardware test script:

```bash
python3 scripts/test_lights.py
```
This will automatically cycle through all 3 LEDs, then provide an interactive terminal controller (`R`, `Y`, `G`, `O`, `T`).

### 3. Background Bridge (Recommended for Arduino)
Standard Arduinos reset if the serial port is repeatedly opened and closed. To prevent this and get instantaneous (0ms) response times, run the background bridge:

```bash
python3 scripts/bridge.py
```
*(You can also keep it running in the background with `nohup python3 scripts/bridge.py > /dev/null 2>&1 &`)*.

---

## ⚙️ Gemini CLI Integration

Add the hook configuration to your Gemini CLI `settings.json` (see [gemini_settings_snippet.json](gemini_settings_snippet.json)):

```json
{
  "hooks": {
    "traffic-light": {
      "SessionStart": [
        { "command": "python3 /Users/alfonsoforcen3/Desktop/TrafficLights_Arduino/scripts/traffic.py G" }
      ],
      "BeforeAgent": [
        { "command": "python3 /Users/alfonsoforcen3/Desktop/TrafficLights_Arduino/scripts/traffic.py Y" }
      ],
      "AfterAgent": [
        { "command": "python3 /Users/alfonsoforcen3/Desktop/TrafficLights_Arduino/scripts/traffic.py G" }
      ],
      "SessionEnd": [
        { "command": "python3 /Users/alfonsoforcen3/Desktop/TrafficLights_Arduino/scripts/traffic.py O" }
      ]
    }
  }
}
```
