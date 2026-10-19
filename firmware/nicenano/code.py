"""nice!nano traffic light: P0.10 green, P1.11 amber, P1.13 red.

LED anodes connect through resistors to GPIO; cathodes connect to GND.
USB/Bluetooth commands: G/Y/R/B/O/T; Q reports the current GPIO output state.
"""
import digitalio
import microcontroller
import time
import usb_cdc
import json
from connection_display import ConnectionDisplay
from pwm_led import PwmLED
from session_count import SessionCount
count_parser = SessionCount()

def output(pin):
    led = digitalio.DigitalInOut(pin)
    led.switch_to_output(value=False)
    return led

def decode_legacy_commands(data):
    """Accept only single-byte legacy commands; malformed RX cannot stop LEDs."""
    return ''.join(chr(value).upper() for value in data
                   if value in b'GYRBOQVTXgyrboqvtx')

# Preserve the original wiring unless a per-unit profile explicitly selects another supported pin.
green_pin = 'P0.10'
green_brightness = 0.5
amber_pin = 'P1.11'
red_pin = 'P1.13'
config = {}
try:
    with open('/hardware_config.json') as config_file:
        config = json.load(config_file)
    green_pin = config.get('green_pin', green_pin)
    green_brightness = config.get('green_brightness', green_brightness)
    amber_pin = config.get('amber_pin', amber_pin)
    red_pin = config.get('red_pin', red_pin)
except OSError:
    pass
if green_pin not in ('P0.10', 'P0.06', 'P0.09', 'P1.11'):
    raise ValueError('Unsupported green pin profile: ' + str(green_pin))
if amber_pin not in ('P1.11', 'P0.10') or red_pin not in ('P1.13', 'P0.09'):
    raise ValueError('Unsupported amber/red wiring profile')
if len(set((green_pin, amber_pin, red_pin))) != 3:
    raise ValueError('LED pins must be distinct')
if config.get('oled_enabled') and set((green_pin, amber_pin, red_pin)) & {'P0.20', 'P0.22'}:
    raise ValueError('OLED pins conflict with LEDs')
green = PwmLED(getattr(microcontroller.pin, green_pin.replace('.', '_')), green_brightness)
amber = output(getattr(microcontroller.pin, amber_pin.replace('.', '_')))
red = output(getattr(microcontroller.pin, red_pin.replace('.', '_')))
port = usb_cdc.data
port.timeout = 0
port.write_timeout = 0.1
mode = "O"
last_blink = time.monotonic()
blink_on = True
connection_display = ConnectionDisplay()
display_phase = None
ble = None
ble_error = None
battery = None
battery_error = None
oled = None
oled_error = None
if config.get('oled_enabled', False):
    try:
        import oled_display as oled
    except Exception as error:
        oled_error = str(error)
try:
    from battery import Battery
    battery = Battery()
except Exception as error:
    battery_error = str(error)
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
    data = (json.dumps({'firmware': 'traffic-nicenano-v1', 'hardware_family': 'nrf52840',
                        'mode': mode,
                        'display_phase': display_phase, 'green_pwm_duty': green.max_duty,
                        'green_pwm_frequency': 5000, 'green_pin': green_pin, 'amber_pin': amber_pin, 'red_pin': red_pin,
                        green_pin: green.value, amber_pin: amber.value, red_pin: red.value,
                        'oled_error': oled.error if oled else oled_error, 'transport': transport,
                        'session_count': count_parser.count if ble and ble.connected else None,
                        'session_count_kind': 'working',
                        'working_provider_mask': count_parser.provider_mask if ble and ble.connected else 0,
                        'ble_name': ble.name if ble else None,
                        'device_id': ble.device_id if ble else None,
                        'identity_protocol': 1,
                        'rename_supported': ble.rename_supported if ble else False,
                        'ble_error': ble_error,
                        'battery': battery.sample() if battery else None,
                        'battery_error': battery_error}) + '\n').encode()
    if transport == 'ble' and ble:
        ble.send(data)
    elif port.connected:
        try:
            port.write(data)
        except OSError:
            pass  # A host disconnect must never stop the LED controller.

set_lights()
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
    if not (ble and ble.connected):
        count_parser.reset()
    for transport, commands in sources:
        if transport == "ble":
            commands = count_parser.feed(commands)
        for cmd in decode_legacy_commands(commands):
            if cmd == 'X' and transport == 'usb':
                microcontroller.reset()  # Local maintenance reset; never exposed over BLE.
            if cmd == "V":
                if battery:
                    battery.sample(force=True)
                report(transport)
            elif cmd == "Q":
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
                    blink_on = True
                    if display_phase == "tracking":
                        set_lights(g=cmd == "G", y=cmd == "Y", r=cmd in "RB")
                report(transport)
    if mode == "B" and time.monotonic() - last_blink >= 0.3:
        blink_on = not blink_on
        last_blink = time.monotonic()
    tracked = (mode == 'G', mode == 'Y', mode == 'R' or (mode == 'B' and blink_on))
    phase, lights = connection_display.frame(time.monotonic(), bool(ble and ble.connected), tracked)
    changed = phase != display_phase
    display_phase = phase
    if (green.value, amber.value, red.value) != lights:
        set_lights(*lights)
    if changed and ble and ble.connected:
        report('ble')
    if oled:
        oled.update(time.monotonic(), mode, bool(ble and ble.connected), count_parser.count, count_parser.provider_mask)
    time.sleep(0.01)
