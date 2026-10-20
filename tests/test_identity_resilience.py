"""Hardware-free BLE boundary checks: every backend is replaced before use."""
import asyncio
import json
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

from scripts import device_identity as identity


class IdentityResilienceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.scanner = types.SimpleNamespace(discover=AsyncMock(
            side_effect=AssertionError('Unexpected Bluetooth discovery')))
        self.backend = types.SimpleNamespace(BleakScanner=self.scanner,
            BleakClient=lambda *args, **kwargs: self.fail('Unexpected Bluetooth client'))
        guard = patch.dict(sys.modules, {'bleak': self.backend})
        guard.start()
        self.addCleanup(guard.stop)

    async def test_invalid_deadlines_fail_before_any_backend_access(self):
        for timeout in (0, -1, float('nan'), float('inf'), True, '12', None):
            with self.subTest(timeout=timeout):
                with self.assertRaises(ValueError):
                    await identity.discover_candidates(timeout)
                with self.assertRaises(ValueError):
                    await identity.inspect_device('chosen', timeout=timeout)
        self.scanner.discover.assert_not_called()

    async def test_backend_scan_is_cancelled_at_outer_deadline(self):
        cancelled = asyncio.Event()
        async def stalled_scan(**kwargs):
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
        self.scanner.discover.side_effect = stalled_scan
        with patch.object(identity, 'SCAN_CLEANUP_TIMEOUT', 0.05):
            with self.assertRaises(asyncio.TimeoutError):
                await asyncio.wait_for(identity.discover_candidates(timeout=0.05), 3)
        self.assertTrue(cancelled.is_set())

    async def test_full_duration_scan_has_bounded_time_to_stop(self):
        async def completed_scan(timeout, **kwargs):
            await asyncio.sleep(timeout)
            # Real backends stop the scanner after the advertised scan interval.
            await asyncio.sleep(0)
            return {}
        self.scanner.discover.side_effect = completed_scan
        self.assertEqual(await identity.discover_candidates(timeout=0.01), [])

    async def test_scan_handles_partial_advertisements_and_deduplicates_addresses(self):
        def entry(address='A', name='Toy', services=None, **fields):
            return (types.SimpleNamespace(address=address, name=name),
                    types.SimpleNamespace(service_uuids=services, **fields))
        self.scanner.discover.side_effect = None
        self.scanner.discover.return_value = {
            'no_services': entry(),
            'bad_services': entry(services=42),
            'bad_item': object(),
            'no_address': entry(address=None, services=[identity.SERVICE_UUID]),
            'unknown_service': entry(services=[None, 42, 'OTHER']),
            'first': entry(services=[None, identity.SERVICE_UUID.upper()], local_name='First'),
            'duplicate': entry(services=[identity.SERVICE_UUID], local_name='Final', rssi=-50),
            'unnamed': entry(address='B', name=42, services=[identity.SERVICE_UUID]),
        }
        self.assertEqual(await identity.discover_candidates(), [
            {'name': '', 'address': 'B', 'rssi': None},
            {'name': 'Final', 'address': 'A', 'rssi': -50},
        ])

    async def test_legacy_inspection_still_allows_missing_uid(self):
        report = {'firmware': 'traffic-nicenano-v1', 'transport': 'ble', 'ble_name': 'Legacy'}
        with patch.object(identity, '_transaction', new=AsyncMock(return_value=report)):
            self.assertIs(await identity.inspect_device('chosen'), report)

    async def test_malformed_reported_uid_is_rejected(self):
        for value in ('other', '', 123, [], True):
            report = {'device_id': value}
            with self.subTest(value=value), patch.object(identity, '_transaction',
                    new=AsyncMock(return_value=report)):
                with self.assertRaisesRegex(ValueError, 'malformed device UID'):
                    await identity.inspect_device('chosen')

    async def test_rename_never_writes_for_invalid_uid_or_capability_types(self):
        uid = '0123456789ABCDEF'
        with patch.object(identity, 'inspect_device', new=AsyncMock()) as inspect, \
                patch.object(identity, '_transaction', new=AsyncMock()) as transaction:
            for value in (None, True, 12, 'other'):
                with self.subTest(uid=value), self.assertRaises(ValueError):
                    await identity.rename_device('chosen', 'Toy', value)
            inspect.assert_not_called()
            for protocol, supported in ((True, True), ('1', True), (1, 'false'), (1, 1), (2, True)):
                inspect.return_value = dict(device_id=uid, identity_protocol=protocol,
                                            rename_supported=supported)
                with self.subTest(protocol=protocol, supported=supported), \
                        self.assertRaisesRegex(ValueError, 'does not support'):
                    await identity.rename_device('chosen', 'Toy', uid)
            transaction.assert_not_called()

    async def test_rename_requires_literal_success_booleans(self):
        uid = '0123456789ABCDEF'
        report = dict(device_id=uid, identity_protocol=1, rename_supported=True)
        with patch.object(identity, 'inspect_device', new=AsyncMock(return_value=report)), \
                patch.object(identity, '_transaction', new=AsyncMock()) as transaction:
            for ok, persistent in ((True, 'false'), ('true', True), (1, True), (True, 1)):
                transaction.return_value = dict(ok=ok, persistent=persistent, ble_name='Toy')
                with self.subTest(ok=ok, persistent=persistent), \
                        self.assertRaisesRegex(ValueError, 'persistently acknowledged'):
                    await identity.rename_device('chosen', 'Toy', uid)
            transaction.return_value = dict(ok=True, persistent=True, ble_name='Toy')
            self.assertTrue((await identity.rename_device('chosen', 'Toy', uid))['ok'])

    async def test_user_cancellation_preserved_when_cleanup_also_cancels(self):
        entered, disconnected = asyncio.Event(), asyncio.Event()
        class Client:
            def __init__(self, *args, **kwargs): pass
            async def connect(self): pass
            async def disconnect(self): disconnected.set()
        self.backend.BleakClient = Client
        async def operation(client):
            entered.set()
            await asyncio.Event().wait()
        async def cleanup(client):
            raise asyncio.CancelledError('backend cleanup cancellation')
        task = asyncio.create_task(identity._with_bounded_client('chosen', operation, 1, cleanup))
        await entered.wait()
        task.cancel('user cancellation')
        with self.assertRaises(asyncio.CancelledError) as caught:
            await task
        # Python 3.9 wait_for may discard the user's cancellation message.
        self.assertNotEqual(str(caught.exception), 'backend cleanup cancellation')
        self.assertTrue(disconnected.is_set())

    async def test_cleanup_cancellation_does_not_replace_original_exchange_error(self):
        disconnected = asyncio.Event()
        class Client:
            def __init__(self, *args, **kwargs): pass
            async def connect(self): pass
            async def disconnect(self): disconnected.set()
        self.backend.BleakClient = Client
        async def operation(client):
            raise OSError('original exchange failure')
        async def cleanup(client):
            raise asyncio.CancelledError('cleanup cancellation')
        with self.assertRaisesRegex(OSError, 'original exchange failure'):
            await identity._with_bounded_client('chosen', operation, 1, cleanup)
        self.assertTrue(disconnected.is_set())

    async def test_cleanup_cancellation_after_success_still_disconnects_and_propagates(self):
        disconnected = asyncio.Event()
        class Client:
            def __init__(self, *args, **kwargs): pass
            async def connect(self): pass
            async def disconnect(self): disconnected.set()
        self.backend.BleakClient = Client
        async def cleanup(client):
            raise asyncio.CancelledError('cleanup cancelled')
        with self.assertRaises(asyncio.CancelledError):
            await identity._with_bounded_client('chosen', AsyncMock(return_value='ok'), 1, cleanup)
        self.assertTrue(disconnected.is_set())

    def test_oversized_frame_cannot_be_accepted_even_with_valid_json_tail(self):
        reports = identity._ReportBuffer()
        self.assertEqual(list(reports.feed(b'x' * (reports.LIMIT + 1))), [])
        self.assertEqual(len(reports.pending), 0)
        self.assertEqual(list(reports.feed(b'{"ok":true}\n{"ok":"next"}\n')),
                         [{'ok': 'next'}])
        oversized = json.dumps({'name': 'x' * reports.LIMIT}).encode() + b'\n'
        self.assertEqual(list(reports.feed(oversized)), [])
        self.assertEqual(list(reports.feed(b'{"ok":true}\n')), [{'ok': True}])

    def test_invalid_and_deeply_nested_reports_do_not_poison_next_frame(self):
        reports = identity._ReportBuffer()
        self.assertEqual(list(reports.feed(b'\xff\n[]\n{"broken"\n')), [])
        self.assertEqual(list(reports.feed(b'[' * 2000 + b'0' + b']' * 2000 + b'\n')), [])
        self.assertEqual(list(reports.feed(b'{"device_id":"01234567"}\n')),
                         [{'device_id': '01234567'}])


if __name__ == '__main__':
    unittest.main()
