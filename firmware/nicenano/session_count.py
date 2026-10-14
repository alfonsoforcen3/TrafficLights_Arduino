"""Incremental N<count>\n and P<provider-mask>\n metadata; legacy single-byte commands pass through."""
class SessionCount:
    def __init__(self):
        self.reset()

    def reset(self):
        self.count = None
        self.provider_mask = 0
        self.kind = None
        self.pending = None

    def feed(self, data):
        commands = bytearray()
        for value in data:
            if self.pending is not None:
                if value == 10:
                    if self.pending and self.pending.isdigit():
                        value_number = int(self.pending)
                        if self.kind == 'N':
                            self.count = value_number
                        elif value_number <= 15:
                            self.provider_mask = value_number
                    self.pending = None
                elif 48 <= value <= 57 and len(self.pending) < 4:
                    self.pending += chr(value)
                else:
                    # Discard malformed metadata until its terminator.
                    self.pending = 'invalid'
            elif value in (ord('N'), ord('P')):
                self.kind = chr(value)
                self.pending = ''
            else:
                commands.append(value)
        return commands
