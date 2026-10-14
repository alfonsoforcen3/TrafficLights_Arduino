import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch


class Bus:
    def __init__(self, *args, **kwargs):
        self.writes = []
        self.locked = False
    def try_lock(self):
        if self.locked:
            return False
        self.locked = True
        return True
    def unlock(self):
        self.locked = False
    def scan(self):
        return [60]
    def writeto(self, address, data):
        assert self.locked
        self.writes.append((address, bytes(data)))


class OledTests(unittest.TestCase):
    def icons(self):
        path = Path(__file__).resolve().parents[1] / 'firmware/nicenano/provider_icons.py'
        spec = importlib.util.spec_from_file_location('tested_icons', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def load(self, bus):
        path = Path(__file__).resolve().parents[1] / 'firmware/nicenano/oled_display.py'
        spec = importlib.util.spec_from_file_location('tested_oled', path)
        module = importlib.util.module_from_spec(spec)
        pins = SimpleNamespace(P0_20='scl', P0_22='sda')
        with patch.dict(sys.modules, {
            'busio': SimpleNamespace(I2C=lambda *a, **kw: bus),
            'microcontroller': SimpleNamespace(pin=pins),
            'provider_icons': self.icons(),
        }):
            spec.loader.exec_module(module)
        return module

    def test_all_statuses_and_disconnect_render_without_errors(self):
        bus = Bus()
        module = self.load(bus)
        for connected in (False, True):
            for mode in 'RYGBO':
                for tick in range(20):
                    module.comment(mode, tick, connected)
                    self.assertIsNone(module.error)
                    self.assertFalse(bus.locked)
        self.assertTrue(any(module.frame))
        before = len(bus.writes)
        module.update(1, 'Y', True)
        module.update(1.01, 'Y', True)
        self.assertEqual(len(bus.writes), before + 9)

    def test_red_cross_eyes_follow_shake(self):
        module = self.load(Bus())
        for tick in range(8):
            module.frame[:] = bytes(1024)
            module.mascot('R', tick)
            dx = (-1, 1, -1, 1, 0, 0, 0, 0)[tick]
            for eye in (11, 35):
                for y in range(5):
                    for x in range(5):
                        lit = bool(module.frame[eye+dx+x+((23+y)//8)*128] & (1 << ((23+y)%8)))
                        self.assertEqual(lit, not (x == y or x == 4-y))

    def test_absent_oled_does_not_break_status_updates(self):
        bus = Bus()
        bus.scan = lambda: []
        module = self.load(bus)
        module.update(1, 'G', True)
        self.assertIsNone(module.error)
        self.assertEqual(bus.writes, [])

    def test_working_footer_changes_but_clawdy_title_stays_fixed(self):
        module = self.load(Bus())
        headers = []
        titles = []
        for count in (None, 0, 1, 2, 42, 9999):
            module.comment('Y', 0, True, count)
            self.assertIsNone(module.error)
            headers.append(bytes(module.frame[:49] + module.frame[128:177]))
            titles.append(bytes(module.frame[56:128] + module.frame[184:256]))
        self.assertEqual(len(set(headers)), len(headers))
        self.assertEqual(len(set(titles)), 1)
        module.comment('Y', 0, False, 42)
        offline = bytes(module.frame)
        module.comment('Y', 0, False, None)
        self.assertEqual(bytes(module.frame), offline)

    def test_every_phrase_fits_and_renders(self):
        module = self.load(Bus())
        for status, options in module.PHRASES.items():
            for index, lines in enumerate(options):
                for line in lines:
                    self.assertLessEqual(len(line)*6-1, 72)
                    self.assertTrue(all(ch in module.font for ch in line))
                module.comment('Y' if status == 'offline' else status,
                               0, status != 'offline', 12, index)
                self.assertIsNone(module.error)
            self.assertEqual(module.status_lines('Y' if status == 'offline' else status,
                             status != 'offline', len(options)), options[0])

    def test_rotation_uses_elapsed_time_and_resets_only_on_status_change(self):
        module = self.load(Bus())
        with patch.object(module, 'comment') as draw:
            module.update(10, 'Y', True, 2)
            self.assertEqual(draw.call_args.args[-1], 0)
            module.update(15.1, 'Y', True, 3)
            self.assertEqual(draw.call_args.args[-1], 1)
            module.update(30.2, 'Y', True, 1)
            self.assertEqual(draw.call_args.args[-1], 4)
            module.update(30.3, 'G', True, 0)
            self.assertEqual(draw.call_args.args[-1], 0)
            module.update(35.4, 'G', False, None)
            self.assertEqual(draw.call_args.args[-1], 0)

    def test_mixed_providers_rotate_and_unknowns_stay_neutral(self):
        module = self.load(Bus())
        self.assertEqual([module.active_provider(7, n) for n in range(4)], [1, 2, 4, 1])
        for mask in range(16):
            for slot in range(4):
                module.comment('Y', 0, True, 12, slot, provider_mask=mask)
                self.assertIsNone(module.error)
        for bitmap in (module.OPENAI, module.GEMINI):
            self.assertEqual(len(bitmap), 36)
            self.assertTrue(all(0 <= row < 2**36 for row in bitmap))
        module.comment('Y', 0, False, None, provider_mask=7)
        offline = bytes(module.frame)
        module.comment('Y', 0, False, None, provider_mask=0)
        self.assertEqual(bytes(module.frame), offline)

    def test_yellow_wip_band_and_separator_stay_clear_of_icons(self):
        module = self.load(Bus())
        def lit(x,y):
            return bool(module.frame[x+(y//8)*128] & (1 << (y%8)))
        for mask in (0,1,2,4,8,7):
            for mode in 'RYGBO':
                for tick in range(8):
                    module.comment(mode,tick,True,1234,provider_mask=mask)
                    self.assertIsNone(module.error)
                    self.assertTrue(any(lit(x,y) for x in range(49) for y in range(2,9)))
                    self.assertFalse(any(lit(x,y) for x in range(49) for y in range(9,16)))
                    self.assertTrue(all(lit(49,y) == (10<=y<=55) for y in range(64)))
                    self.assertTrue(any(lit(x,y) for x in range(49) for y in range(16,64)))
