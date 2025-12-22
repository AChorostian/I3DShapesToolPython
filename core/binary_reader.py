import struct


class BinaryReader:
    pos = 0
    data = None

    def __init__(self, data: bytes):
        self.data = data

    def read(self, fmt):
        size = struct.calcsize(fmt)
        val = struct.unpack_from(fmt, self.data, self.pos)
        self.pos += size
        return val[0] if len(val) == 1 else val

    def read_bytes(self, n):
        b = self.data[self.pos:self.pos + n]
        self.pos += n
        return b
    
    def align(self, alignment=4):
        mask = alignment - 1
        self.pos = (self.pos + mask) & ~mask

    def remaining(self):
        return self.data[self.pos:]