import asyncio
import unittest
from scripts.ble_transport import BluetoothLink, RX_UUID


class SinglePendingClient:
    """Mimic the CoreBluetooth backend's single future per characteristic."""
    is_connected = True
    def __init__(self):
        self.active = 0
        self.writes = []
    async def write_gatt_char(self, uuid, data, response):
        if self.active:
            raise KeyError(29)
        self.active += 1
        try:
            await asyncio.sleep(.005)
            self.writes.append((uuid, data, response))
        finally:
            self.active -= 1


class BluetoothWriteTests(unittest.IsolatedAsyncioTestCase):
    def link(self):
        return BluetoothLink('test', lambda: 'Y', lambda report: None)

    async def test_concurrent_hooks_heartbeat_and_metadata_never_overlap(self):
        link = self.link()
        client = link.client = SinglePendingClient()
        packets = [b'Y', b'N12\n', b'P7\n', b'G', b'V'] * 5
        await asyncio.gather(*(link.write(packet) for packet in packets))
        self.assertEqual(client.writes, [(RX_UUID, packet, True) for packet in packets])

    async def test_disconnect_is_checked_after_waiting_for_lock(self):
        link = self.link()
        link._write_lock = asyncio.Lock()
        client = link.client = SinglePendingClient()
        await link._write_lock.acquire()
        task = asyncio.create_task(link.write(b'Y'))
        await asyncio.sleep(0)
        client.is_connected = False
        link._write_lock.release()
        with self.assertRaises(ConnectionError):
            await task
        self.assertEqual(client.writes, [])

    async def test_cancellation_releases_lock_for_next_write(self):
        link = self.link()
        client = link.client = SinglePendingClient()
        task = asyncio.create_task(link.write(b'Y'))
        while not client.active:
            await asyncio.sleep(0)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        await link.write(b'Q')
        self.assertEqual(client.writes, [(RX_UUID, b'Q', True)])
