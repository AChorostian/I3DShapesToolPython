import struct


CRYPT_BLOCK_SIZE = 64  # bytes



MASK32 = 0xFFFFFFFF

def u32(x):
    return x & MASK32

def Rol(val, bits):
    return ((val & MASK32) << bits | (val & MASK32) >> (32 - bits)) & MASK32

def Ror(val, bits):
    return ((val & MASK32) >> bits | (val & MASK32) << (32 - bits)) & MASK32

def shuffle1(k, i1, i2, i3, i4):
    k[i3] ^= Rol(k[i2] + k[i1], 7)
    k[i4] ^= Rol(k[i3] + k[i1], 9)
    k[i2] ^= Rol(k[i3] + k[i4], 13)
    k[i1] ^= Ror(k[i2] + k[i4], 14)

def shuffle2(k, i1, i2, i3, i4):
    k[i3] ^= Rol(k[i2] + k[i1], 7)
    k[i4] ^= Rol(k[i2] + k[i3], 9)
    k[i1] ^= Rol(k[i3] + k[i4], 13)
    k[i2] ^= Ror(k[i4] + k[i1], 14)

class I3DCipher:
    def __init__(self, seed: int, key_const: list[int]):
        self.key = [key_const[(seed << 4) + i] & 0xFFFFFFFF for i in range(16)]
        self.key[0x8] = 0  # block counter low
        self.key[0x9] = 0  # block counter high
        self.block_index = 0  # track current block for streaming

    def get_key_by_index_block(self, base_key, block_index):
        temp_key = base_key.copy()
        temp_key[8] = block_index & 0xFFFFFFFF
        temp_key[9] = (block_index >> 32) & 0xFFFFFFFF
        return temp_key

    def process_blocks(self, buf, key):
        if len(buf) % 16 != 0:
            raise ValueError("Expecting 16 uint blocks")
        block_counter = key[8] | (key[9] << 32)
        temp_key = key.copy()
        for i in range(0, len(buf), 16):
            temp_key[:] = key[:]
            for _ in range(10):
                shuffle1(temp_key, 0x0, 0xC, 0x4, 0x8)
                shuffle1(temp_key, 0x5, 0x1, 0x9, 0xD)
                shuffle1(temp_key, 0xA, 0x6, 0xE, 0x2)
                shuffle1(temp_key, 0xF, 0xB, 0x3, 0x7)
                shuffle2(temp_key, 0x3, 0x0, 0x1, 0x2)
                shuffle2(temp_key, 0x4, 0x5, 0x6, 0x7)
                shuffle1(temp_key, 0xA, 0x9, 0xB, 0x8)
                shuffle2(temp_key, 0xE, 0xF, 0xC, 0xD)
            for j in range(len(key)):
                buf[i + j] ^= u32(key[j] + temp_key[j])
            block_counter += 1
            key[8] = u32(block_counter)
            key[9] = u32(block_counter >> 32)

    def decrypt_stream(self, data: bytes) -> bytes:
        out = bytearray()
        for offset in range(0, len(data), CRYPT_BLOCK_SIZE):
            chunk = data[offset:offset + CRYPT_BLOCK_SIZE]
            block = bytearray(CRYPT_BLOCK_SIZE)
            block[:len(chunk)] = chunk
            buf = list(struct.unpack("<16I", block))
            key = self.get_key_by_index_block(self.key, self.block_index)
            self.process_blocks(buf, key)
            out.extend(struct.pack("<16I", *buf)[:len(chunk)])
            self.block_index += 1
        return bytes(out)