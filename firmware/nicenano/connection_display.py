"""Nonblocking Bluetooth connection lights; tracked state survives animations."""
class ConnectionDisplay:
    SHOW = ((False, False, True), (False, True, False), (True, False, False),
            (False, False, True), (False, True, False), (True, False, False))
    def __init__(self):
        self.connected = False
        self.started = 0
        self.search_started = 0

    def frame(self, now, connected, tracked):
        if connected != self.connected:
            self.connected = connected
            if connected:
                self.started = now
            else:
                self.search_started = now
        if not connected:
            on = int((now - self.search_started) / 0.4) % 2 == 0
            return 'searching', (on, on, on)
        index = int((now - self.started) / 0.16)
        if index < len(self.SHOW):
            return 'connected_show', self.SHOW[index]
        return 'tracking', tracked
