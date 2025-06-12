set1 = bytes(range(32)).decode('ascii')
set2 = '!"#$%&\'()*+,-./:;<=>?@[\\]^_'


def add_inverse_lookup(codepage: dict) -> None:
    all_chars = list(codepage.keys())
    for char in all_chars:
        code = codepage[char]
        codepage[bytes(code)] = char


def encode_text_mode(msg: str, codepage: dict, magic: bytes, multiset: bool) -> tuple[bytes, int]:
    try:
        raw = sum([codepage[char] for char in msg], [])
    except KeyError:
        raise ValueError('Incompatible character in msg')

    l_packable = (len(raw) // 3) * 3

    enc = b''
    if l_packable > 0:
        enc += magic
        topack = raw[:l_packable]
        enc += pack_words(topack)
        enc += b'\xFE'
    else:
        topack = []

    if multiset:
        toascii = msg[len(list(tokenize(topack))):]
    else:
        toascii = msg[len(topack):]

    enc += toascii.encode('datamatrix.ascii')

    return enc, len(enc)


def decode_text_mode(enc: bytes, codepage: dict, magic: bytes, multiset: bool) -> tuple[str, int]:
    enc = bytes(enc)
    magic = list(magic)[0]
    if enc[0] != magic:
        msg = enc.decode('datamatrix.ascii')
        return msg, len(msg)

    enc = enc[1:]

    pos = enc[::2].find(b'\xFE')
    words = enc[:2 * pos]
    remainder = enc[2 * pos + 1:]

    raw = unpack_words(words)
    if multiset is True:
        msg = ''.join([codepage[code] for code in tokenize(raw)])
    else:
        msg = ''.join([codepage[bytes([code])] for code in raw])
    msg += bytes(remainder).decode('datamatrix.ascii')

    return msg, len(msg)


def pack_words(raw: list[int] | bytes) -> bytes:
    if len(raw) % 3 != 0:
        raise ValueError('Length of "raw" must be integer multiple of 3')

    raw = list(raw)
    enc = []
    while len(raw) > 0:
        word = ((raw.pop(0) * 40 ** 2) +
                (raw.pop(0) * 40 ** 1) +
                (raw.pop(0) * 40 ** 0) +
                1)
        enc += [word >> 8, word & 0xFF]

    return bytes(enc)


def unpack_words(words: list[int] | bytes) -> bytes:
    if len(words) % 2 != 0:
        raise ValueError('Length of "words" must be even')

    words = list(words)
    raw = []
    while len(words) >= 2:
        word = ((words.pop(0) << 8) +
                (words.pop(0) << 0))
        word -= 1
        raw += [word // 40 ** 2,
                (word % 40 ** 2) // 40 ** 1,
                ((word % 40 ** 2) % 40 ** 1) // 40 ** 0]

    return bytes(raw)


def tokenize(enc: list[int] | bytes):
    buffer = b''
    for code in iter(enc):
        if buffer:
            yield buffer + bytes([code])
            buffer = b''
        elif code >= 3:
            yield bytes([code])
        else:
            buffer = bytes([code])
