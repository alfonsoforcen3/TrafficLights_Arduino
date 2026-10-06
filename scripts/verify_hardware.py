#!/usr/bin/env python3
"""Check real board acknowledgements; briefly overrides LEDs, then restores tracking."""
import argparse
import json
import socket
import time

def request(payload):
    with socket.create_connection(('127.0.0.1', 8765), 3) as connection:
        connection.sendall(json.dumps(payload).encode())
        return json.loads(connection.recv(8192))

def verify(transport):
    try:
        for mode in 'RYGBO':
            request({'action': 'hardware_test', 'state': mode})
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                result = request({'action': 'status'})
                report = result.get('firmware_report') or {}
                if (result['hardware_connected'] and report.get('mode') == mode
                        and report.get('display_phase') in (None, 'tracking')):
                    if transport and report.get('transport') != transport:
                        raise AssertionError('Board acknowledgement used the wrong transport: ' + str(report))
                    if mode != 'B':
                        expected = [mode == 'G', mode == 'Y', mode == 'R']
                        assert [report[report.get('green_pin', 'P0.10')], report['P1.11'], report['P1.13']] == expected, report
                    print('Confirmed', mode, report, flush=True)
                    time.sleep(1)
                    break
                time.sleep(.15)
            else:
                raise AssertionError('Board did not acknowledge ' + mode + ': ' + str(result))
    finally:
        request({'action': 'resume'})
    print('Tracking restored. A human must also confirm the LEDs physically lit.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transport', choices=['ble', 'usb'], default='ble')
    args = parser.parse_args()
    verify(args.transport)
