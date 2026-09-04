import machine
import time

class LCD:
    def __init__(self, i2c, addr=None, blen=1, cols=16, rows=2,
                 retries=3, nibble_delay_ms=5, after_clear_ms=3):
        self.bus = i2c
        self.addr = self.scanAddress(addr)
        self.blen = blen
        self.cols = cols
        self.rows = rows
        self.retries = retries
        self.nibble_delay_ms = nibble_delay_ms
        self.after_clear_ms = after_clear_ms
        self._locked = False

        self.send_command(0x33)
        time.sleep_ms(5)
        self.send_command(0x32)
        time.sleep_ms(5)
        self.send_command(0x28)
        time.sleep_ms(5)
        self.send_command(0x0C)
        time.sleep_ms(5)
        self.send_command(0x01)
        time.sleep_ms(self.after_clear_ms)
        self.bus.writeto(self.addr, bytearray([0x08 if self.blen else 0x00]))

    def scanAddress(self, addr):
        devices = self.bus.scan()
        if len(devices) == 0:
            raise Exception("No LCD found")
        if addr is not None:
            if addr in devices:
                return addr
            else:
                raise Exception("LCD at 0x%02X not found" % addr)
        elif 0x27 in devices:
            return 0x27
        elif 0x3F in devices:
            return 0x3F
        else:
            return devices[0]

    def _acquire(self):
        while self._locked:
            time.sleep_ms(1)
        self._locked = True

    def _release(self):
        self._locked = False

    def write_word(self, data):
        temp = data
        if self.blen == 1:
            temp |= 0x08
        else:
            temp &= 0xF7

        last_exc = None
        for attempt in range(self.retries):
            try:
                self.bus.writeto(self.addr, bytearray([temp]))
                return
            except OSError as e:
                last_exc = e
                time.sleep_ms(5 + attempt * 5)
        raise last_exc

    def send_command(self, cmd):
        buf = cmd & 0xF0
        buf |= 0x04
        self.write_word(buf)
        time.sleep_ms(self.nibble_delay_ms)
        buf &= 0xFB
        self.write_word(buf)

        buf = (cmd & 0x0F) << 4
        buf |= 0x04
        self.write_word(buf)
        time.sleep_ms(self.nibble_delay_ms)
        buf &= 0xFB
        self.write_word(buf)

    def send_data(self, data):
        buf = data & 0xF0
        buf |= 0x05
        self.write_word(buf)
        time.sleep_ms(self.nibble_delay_ms)
        buf &= 0xFB
        self.write_word(buf)

        buf = (data & 0x0F) << 4
        buf |= 0x05
        self.write_word(buf)
        time.sleep_ms(self.nibble_delay_ms)
        buf &= 0xFB
        self.write_word(buf)

    def clear(self):
        self.send_command(0x01)
        time.sleep_ms(self.after_clear_ms)

    def openlight(self):
        self.bus.writeto(self.addr, bytearray([0x08]))

    def write(self, x, y, s):
        if x < 0:
            x = 0
        if x >= self.cols:
            x = self.cols - 1
        if y < 0:
            y = 0
        if y >= self.rows:
            y = self.rows - 1

        addr = 0x80 + 0x40 * y + x
        self._acquire()
        try:
            self.send_command(addr)
            for ch in s:
                self.send_data(ord(ch))
        finally:
            self._release()

    def safe_write_line(self, row, text):
        if row < 0: row = 0
        if row >= self.rows: row = self.rows - 1
        if len(text) > self.cols:
            text = text[:self.cols]
        else:
            text = text + " " * (self.cols - len(text))

        addr = 0x80 + 0x40 * row
        self._acquire()
        try:
            self.send_command(addr)
            for ch in text:
                self.send_data(ord(ch))
        finally:
            self._release()

    def message(self, text):
        lines = text.split("\n")
        out_lines = []
        for r in range(self.rows):
            if r < len(lines):
                ln = lines[r]
            else:
                ln = ""
            if len(ln) > self.cols:
                ln = ln[:self.cols]
            else:
                ln = ln + " " * (self.cols - len(ln))
            out_lines.append(ln)

        self._acquire()
        try:
            self.send_command(0x01)
            time.sleep_ms(self.after_clear_ms)
            self.send_command(0x80)
            for ch in out_lines[0]:
                self.send_data(ord(ch))
            if self.rows > 1:
                self.send_command(0xC0)
                for ch in out_lines[1]:
                    self.send_data(ord(ch))
        finally:
            self._release()
