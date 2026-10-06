import importlib.util
from pathlib import Path
import unittest
path = Path(__file__).resolve().parents[1] / 'firmware/nicenano/connection_display.py'
spec = importlib.util.spec_from_file_location('connection_display', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ConnectionDisplayTests(unittest.TestCase):
    def test_search_blinks_all_together(self):
        d = module.ConnectionDisplay()
        self.assertEqual(d.frame(0, False, (False, True, False)), ('searching', (True, True, True)))
        self.assertEqual(d.frame(.5, False, (False, True, False)), ('searching', (False, False, False)))

    def test_connection_show_restores_latest_work_and_does_not_restart(self):
        d = module.ConnectionDisplay()
        self.assertEqual(d.frame(5, True, (False, True, False))[0], 'connected_show')
        self.assertEqual(d.frame(6.1, True, (False, True, False)), ('tracking', (False, True, False)))
        self.assertEqual(d.frame(7, True, (False, False, True)), ('tracking', (False, False, True)))

    def test_reconnection_replays_show_without_inventing_green(self):
        d = module.ConnectionDisplay()
        d.frame(1, True, (False, True, False))
        self.assertEqual(d.frame(4, False, (False, True, False))[0], 'searching')
        self.assertEqual(d.frame(5, True, (False, True, False))[0], 'connected_show')
        self.assertEqual(d.frame(7, True, (False, False, False)), ('tracking', (False, False, False)))
