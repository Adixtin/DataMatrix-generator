import codecs
from .codec_common import add_inverse_lookup
from .codec_common import encode_text_mode, decode_text_mode

X12 = '\r*> 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

codepage = {char: [code] for char, code in zip(X12, range(40))}
add_inverse_lookup(codepage)


def encode(msg: str) -> tuple[bytes, int]:
    enc, length = encode_text_mode(msg, codepage, b'\xEE', False)

    return enc, length


def decode(enc: bytes | bytearray) -> tuple[str, int]:
    msg, length = decode_text_mode(enc, codepage, b'\xEE', False)

    return msg, length


def search_codec(encoding_name: str) -> codecs.CodecInfo | None:
    if encoding_name != 'datamatrix.x12':
        return None

    return codecs.CodecInfo(encode,
                            decode,
                            name='datamatrix.X12')


codecs.register(search_codec)
