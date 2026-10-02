import importlib.util
import json
import sys
import time
import types
import unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from dashboard import Dashboard

class DashboardTests(unittest.TestCase):
    def test_disconnected_and_missing_samples_are_stale(self):
        report = {'battery': {'sensor_voltage': .25}, 'private_prompt': 'secret'}
        online = [True]
        dash = Dashboard(lambda: report, lambda: online[0])
        self.assertTrue(dash.status()['stale'])
        dash.received(report)
        self.assertFalse(dash.status()['stale'])
        self.assertNotIn('private_prompt', dash.status())
        online[0] = False
        self.assertTrue(dash.status()['stale'])
        online[0] = True
        dash.last_seen = time.time() - 100
        self.assertTrue(dash.status()['stale'])
        dash.received(None)
        self.assertEqual(dash.status()['history'], [])

    def test_http_rejects_foreign_host_and_private_routes(self):
        dash = Dashboard(lambda: None, lambda: False)
        server = dash.start(0)
        base = 'http://127.0.0.1:' + str(server.server_port)
        try:
            req = Request(base + '/api/battery', headers={'Host':'127.0.0.1:'+str(server.server_port)})
            with urlopen(req) as result:
                self.assertTrue(json.load(result)['stale'])
                self.assertIsNone(result.headers.get('Access-Control-Allow-Origin'))
            for path, host, code in [('/api/battery','evil.example',403),('/../bridge.py','127.0.0.1:'+str(server.server_port),404)]:
                with self.assertRaises(HTTPError) as error:
                    urlopen(Request(base+path, headers={'Host':host}))
                self.assertEqual(error.exception.code, code)
        finally:
            server.shutdown(); server.server_close()

    def test_uncalibrated_adc_never_claims_battery_percent(self):
        adc = types.SimpleNamespace(value=32768, reference_voltage=3.3)
        replacements = {'analogio':types.SimpleNamespace(AnalogIn=lambda _: adc),
                        'microcontroller':types.SimpleNamespace(pin=types.SimpleNamespace(P0_04=4))}
        previous = {name:sys.modules.get(name) for name in replacements}
        sys.modules.update(replacements)
        try:
            path = Path(__file__).resolve().parents[1] / 'firmware/nicenano/battery.py'
            spec = importlib.util.spec_from_file_location('battery_test', path)
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            battery = module.Battery()
            sample = battery.sample()
            self.assertAlmostEqual(sample['sensor_voltage'], 1.65, places=3)
            self.assertIsNone(sample['estimated_percent'])
            self.assertIsNone(sample['voltage'])
            self.assertIsNone(sample['charging'])
            battery.ratio = 2.4
            self.assertTrue(battery.sample(True)['measurement_valid'])
            battery.ratio = 10
            self.assertIsNone(battery.sample(True)['estimated_percent'])
        finally:
            for name, original in previous.items():
                if original is None:sys.modules.pop(name, None)
                else:sys.modules[name] = original
