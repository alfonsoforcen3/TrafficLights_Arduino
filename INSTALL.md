# 🛠️ Installation & Setup Guide

This guide walks you through setting up the **Arduino Traffic Light** system from scratch on any computer (macOS, Linux, or Windows).

---

## 📋 1. Hardware Requirements

* **1x Arduino Board** (Uno, Nano, or compatible clone with CH340 / FTDI / Atmega16U2).
* **3x LEDs**: Green, Yellow, Red (5mm standard).
* **3x Resistors**: 220 Ω to 330 Ω (one for each LED).
* **1x USB Data Cable** (verify it is a data cable, not charge-only).
* Breadboard and jumper wires.

### Wiring Diagram

```
         Arduino (Uno / Nano)
       ┌────────────────────────┐
       │          Digital Pin  9 ├──[220Ω]──▶|── Green LED  ──┐
       │          Digital Pin 10 ├──[220Ω]──▶|── Yellow LED ──┤
       │          Digital Pin 11 ├──[220Ω]──▶|── Red LED    ──┤
       │                     GND ├────────────────────────────┘
       │                        │
       │   USB-B / Mini / C  ───┼──────►  to Computer
       └────────────────────────┘

    ▶|  = LED. The anode (longer leg) connects to the resistor/Pin.
               The cathode (shorter leg, flat edge) connects to GND.
```

---

## 💻 2. Software Prerequisites

### A. Python & PySerial
Ensure Python 3 is installed, then install `pyserial`:
```bash
pip3 install pyserial
```

### B. Serial Port Access (Linux only)
If on Linux, ensure your user is in the `dialout` group:
```bash
sudo usermod -a -G dialout $USER
```

---

## ⚡ 3. Flash the Firmware

### Option A: Using the Arduino IDE (Recommended for beginners)
1. Open the Arduino IDE.
2. Open [`firmware/traffic_light/traffic_light.ino`](firmware/traffic_light/traffic_light.ino).
3. Connect your Arduino via USB.
4. Under **Tools**:
   * **Board**: Select *Arduino Uno* (or *Arduino Nano*).
   * **Port**: Select your board's serial port (e.g. `/dev/cu.usbserial-*` on Mac, `/dev/ttyUSB*` on Linux, `COM*` on Windows).
5. Click **Upload**.
6. The board will execute an automatic visual startup test (**Red ➔ Yellow ➔ Green ➔ Flash**) confirming that all pins and LEDs are functional.

### Option B: Using `arduino-cli`
```bash
arduino-cli compile --fqbn arduino:avr:uno firmware/traffic_light
arduino-cli upload -p /dev/cu.usbserial-1120 --fqbn arduino:avr:uno firmware/traffic_light
```

---

## 🚀 4. Start the Background Bridge

Standard Arduinos trigger an auto-reset when a new serial connection is opened. The background bridge keeps the USB serial connection open 24/7 so commands execute with **instant (<2ms) response times**.

Start the bridge:
```bash
python3 scripts/bridge.py
```
To run it continuously in the background:
```bash
nohup python3 scripts/bridge.py > /dev/null 2>&1 &
```

---

## 🚦 5. Verify Hardware

Run the interactive hardware tester to cycle all LEDs:
```bash
python3 scripts/test_lights.py
```
You can press `R`, `B` (blinking red), `Y`, `G`, `O`, or `T` to toggle the lights manually.

---

## 🔗 6. Enable Lifecycle Hooks

Run the safe hook manager from the project root:
```bash
./manage_hooks.py enable
```

### To Check Status:
```bash
./manage_hooks.py status
```

### To Revert / Disable at Any Time:
```bash
./manage_hooks.py disable
```
*(This completely removes the hook configuration and turns off the light).*
