import codecs
from .codec_common import set1, set2, add_inverse_lookup
from .codec_common import encode_text_mode, decode_text_mode

set0 = ' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
set3 = '`abcdefghijklmnopqrstuvwxyz{|}~' + b'\x7f'.decode('ascii')

codepage = {char: [code] for char, code in zip(set0, range(3, 40))}
codepage = {**codepage,
            **{char: [0, code] for char, code in zip(set1, range(40))}}
codepage = {**codepage,
            **{char: [1, code] for char, code in zip(set2, range(40))}}
codepage = {**codepage,
            **{char: [2, code] for char, code in zip(set3, range(40))}}

add_inverse_lookup(codepage)


def encode(msg: str) -> tuple[bytes, int]:
    return encode_text_mode(msg, codepage, b'\xE6', True)


def decode(enc) -> tuple[str, int]:
    msg, length = decode_text_mode(enc, codepage, b'\xE6', True)

    return msg, length


def search_codec(encoding_name: str) -> codecs.CodecInfo | None:
    if encoding_name != 'datamatrix.c40':
        return None

    return codecs.CodecInfo(encode,
                            decode,
                            name='datamatrix.C40')


codecs.register(search_codec)