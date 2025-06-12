import codecs


def pack(ascii: bytes) -> bytes:
    assert len(ascii) % 4 == 0

    raw = [code & 0x3F for code in ascii if 31 <= code <= 94]
    if len(raw) < len(ascii):
        raise ValueError('Invalid EDIFACT')

    packed = []
    while len(raw) > 0:
        word = ((raw.pop(0) << 18) +
                (raw.pop(0) << 12) +
                (raw.pop(0) << 6) +
                (raw.pop(0)))
        packed += [word >> 16, (word >> 8) & 0xFF, (word >> 0) & 0xFF]

    return bytes(packed)


def encode(msg: str) -> tuple[bytes, int]:
    l_packable = ((len(msg) + 1) // 4) * 4

    enc = b''
    if l_packable > 0:
        enc += b'\xF0'
        enc += pack(msg[:l_packable - 1].encode('ascii') + b'\x1F')


    l_remaining = min(len(msg), len(msg) + 1 - l_packable)
    enc = enc + msg[len(msg) - l_remaining:].encode('datamatrix.ascii')

    return enc, len(enc)


def decode(enc: bytes | bytearray) -> tuple[str, int]:
    edifact = list(enc)
    if edifact[0] != 0xF0:
        if len(edifact) <= 2:
            msg = bytes(edifact).decode('datamatrix.ascii')
            return msg, len(msg)
        else:
            raise ValueError(f'{enc} is not EDIFACT encoded')

    raw = []
    edifact.pop(0)
    ascii = b''
    while len(edifact) > 0:
        word = edifact.pop(0) << 16
        word += edifact.pop(0) << 8
        word += edifact.pop(0) << 0

        newraw = [(word >> 18) & 0x3F, (word >> 12) & 0x3F,
                  (word >> 6) & 0x3F, (word >> 0) & 0x3F]
        if 0x1F in newraw:
            raw += newraw[:newraw.index(0x1F)]
            ascii = bytes(edifact)
            break
        else:
            raw += newraw

    msg = bytes([code if code >= 0x20 else code | 0x40
                 for code in raw]).decode('ascii')

    msg += ascii.decode('datamatrix.ascii')

    return msg, len(msg)


def search_codec(encoding_name: str) -> codecs.CodecInfo | None:
    if encoding_name != 'datamatrix.edifact':
        return None

    return codecs.CodecInfo(encode, decode,
                            name='datamatrix.edifact')


codecs.register(search_codec)