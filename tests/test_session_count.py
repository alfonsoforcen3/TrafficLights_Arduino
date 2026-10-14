import importlib.util
from pathlib import Path
import unittest

source = Path(__file__).resolve().parents[1] / 'firmware/nicenano/session_count.py'
spec = importlib.util.spec_from_file_location('session_count', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CountTests(unittest.TestCase):
    def test_every_split_preserves_commands_and_count(self):
        data = b'YN12\nGQ'
        for split in range(len(data)+1):
            parser = module.SessionCount()
            result = parser.feed(data[:split]) + parser.feed(data[split:])
            self.assertEqual(result, b'YGQ')
            self.assertEqual(parser.count, 12)

    def test_malformed_metadata_cannot_act_as_a_color_command(self):
        parser = module.SessionCount()
        self.assertEqual(parser.feed(b'N2\nNRYG\nN99999\nQ'), b'Q')
        self.assertEqual(parser.count, 2)
        parser.reset()
        self.assertIsNone(parser.count)
        self.assertEqual(parser.feed(b'N0\nR'), b'R')
        self.assertEqual(parser.count, 0)

    def test_legacy_commands_and_reconnection(self):
        parser = module.SessionCount()
        self.assertEqual(parser.feed(b'RYGBOQV'), b'RYGBOQV')
        parser.feed(b'N123')
        parser.reset()
        self.assertEqual(parser.feed(b'GN1\nQ'), b'GQ')
        self.assertEqual(parser.count, 1)

    def test_bridge_excludes_ready_waiting_and_error_chats(self):
        from scripts import bridge
        from unittest.mock import patch
        with patch.object(bridge, 'active_sessions', {
            'codex:a': {'state': 'Y'}, 'claude:b': {'state': 'Y'},
            'codex:c': {'state': 'G'}, 'claude:d': {'state': 'B'},
            'codex:e': {'state': 'R'},
        }):
            self.assertEqual(bridge.working_session_count(), 2)
            bridge.active_sessions['codex:a']['state'] = 'G'
            self.assertEqual(bridge.working_session_count(), 1)
            bridge.active_sessions['claude:b']['state'] = 'B'
            self.assertEqual(bridge.working_session_count(), 0)

    def test_provider_metadata_fragmentation_and_invalid_mask(self):
        data = b'N12\nP7\nYQ'
        for split in range(len(data)+1):
            parser = module.SessionCount()
            result = parser.feed(data[:split]) + parser.feed(data[split:])
            self.assertEqual(result, b'YQ')
            self.assertEqual(parser.count, 12)
            self.assertEqual(parser.provider_mask, 7)
        self.assertEqual(parser.feed(b'P999\nPRYG\nQ'), b'Q')
        self.assertEqual(parser.provider_mask, 7)
        parser.reset()
        self.assertEqual(parser.provider_mask, 0)

    def test_provider_identity_is_application_not_model(self):
        from scripts import bridge
        from unittest.mock import patch
        with patch.object(bridge, 'active_sessions', {
            'claude:a': {'state': 'Y'}, 'codex:b': {'state': 'Y'},
            'gemini:c': {'state': 'G'}, 'cursor:d': {'state': 'Y'},
        }):
            self.assertEqual(bridge.working_provider_mask(), 11)
            bridge.active_sessions['gemini:c']['state'] = 'Y'
            self.assertEqual(bridge.working_provider_mask(), 15)
            bridge.active_sessions['claude:a']['state'] = 'B'
            self.assertEqual(bridge.working_provider_mask(), 14)
