"""nice!nano traffic light: P0.10 green, P1.11 amber, P1.13 red.

LED anodes connect through resistors to GPIO; cathodes connect to GND.
USB/Bluetooth commands: G/Y/R/B/O/T; Q reports the current GPIO output state.
"""
import digitalio
import microcontroller
import time
import usb_cdc
import json

def output(pin):
    led = digitalio.DigitalInOut(pin)
    led.switch_to_output(value=False)
    return led

green = output(microcontroller.pin.P0_10)
amber = output(microcontroller.pin.P1_11)
red = output(microcontroller.pin.P1_13)
port = usb_cdc.data
port.timeout = 0
port.write_timeout = 0.1
mode = "G"
last_blink = time.monotonic()
ble = None
ble_error = None
try:
    from ble_link import Link
    ble = Link()
except Exception as error:
    ble_error = str(error)

def set_lights(g=False, y=False, r=False):
    green.value = False
    amber.value = False
    red.value = False
    green.value = g
    amber.value = y
    red.value = r

def report(transport='usb'):
    data = (json.dumps({'firmware': 'traffic-nicenano-v1', 'mode': mode,
                        'P0.10': green.value, 'P1.11': amber.value,
                        'P1.13': red.value, 'transport': transport,
                        'ble_name': ble.name if ble else None,
                        'ble_error': ble_error}) + '\n').encode()
    if transport == 'ble' and ble:
        ble.send(data)
    elif port.connected:
        try:
            port.write(data)
        except OSError:
            pass  # A host disconnect must never stop the LED controller.

set_lights(g=True)
was_connected = False
while True:
    connected = port.connected
    if connected and not was_connected:
        try:
            port.write(b"TRAFFIC_LIGHT_READY\n")
        except OSError:
            pass
    was_connected = connected
    sources = []
    if port.in_waiting:
        sources.append(('usb', port.read(port.in_waiting)))
    if ble:
        sources.append(('ble', ble.poll()))
    for transport, commands in sources:
        for cmd in commands.decode('utf-8').upper():
            if cmd == 'X' and transport == 'usb':
                microcontroller.reset()  # Local maintenance reset; never exposed over BLE.
            if cmd == "Q":
                report(transport)
            elif cmd == "T":
                for color in "RYG":
                    set_lights(g=color == "G", y=color == "Y", r=color == "R")
                    time.sleep(0.5)
                mode = "G"
                report(transport)
            elif cmd in "GYRBO":
                # Repeated heartbeat commands must not restart the blink timer.
                if cmd != mode:
                    mode = cmd
                    last_blink = time.monotonic()
                    set_lights(g=cmd == "G", y=cmd == "Y", r=cmd in "RB")
                report(transport)
    if mode == "B" and time.monotonic() - last_blink >= 0.3:
        red.value = not red.value
        last_blink = time.monotonic()
    time.sleep(0.01)
