__all__ = ['encode', 'decode', 'search_codec']


import codecs
from typing import Tuple, Optional

DIGITS = '0123456789'
DOUBLE_DIGIT_OFFSET = 130
MAX_DOUBLE_DIGIT_VALUE = 230
ASCII_OFFSET = 1


def encode(msg):
    if not isinstance(msg, str):
        raise TypeError("Input must be a string")

    encoded = []
    i = 0

    while i < len(msg):
        if (i + 1 < len(msg) and
                msg[i] in DIGITS and
                msg[i + 1] in DIGITS):
            digit_pair = int(msg[i:i + 2])
            encoded.append(DOUBLE_DIGIT_OFFSET + digit_pair)
            i += 2
        else:
            ascii_val = ord(msg[i])
            if ascii_val > 127:
                raise UnicodeEncodeError('datamatrix.ascii', msg, i, i + 1,
                                         f"Non-ASCII character '{msg[i]}' at position {i}")
            encoded.append(ascii_val + ASCII_OFFSET)
            i += 1

    return bytes(encoded), len(encoded)


def decode(code):
    if not isinstance(code, (bytes, bytearray)):
        raise TypeError("Input must be bytes or bytearray")

    decoded_chars = []

    for i, byte_val in enumerate(code):
        if DOUBLE_DIGIT_OFFSET <= byte_val < MAX_DOUBLE_DIGIT_VALUE:
            digit_value = byte_val - DOUBLE_DIGIT_OFFSET
            if digit_value > 99:
                raise UnicodeDecodeError('datamatrix.ascii', code, i, i + 1,
                                         f"Invalid double-digit encoding: {byte_val}")
            decoded_chars.append(f'{digit_value:02d}')
        elif byte_val >= ASCII_OFFSET:
            ascii_val = byte_val - ASCII_OFFSET
            if ascii_val > 127:
                raise UnicodeDecodeError('datamatrix.ascii', code, i, i + 1,
                                         f"Invalid ASCII value: {ascii_val}")
            decoded_chars.append(chr(ascii_val))
        else:
            raise UnicodeDecodeError('datamatrix.ascii', code, i, i + 1,
                                     f"Invalid encoded byte: {byte_val}")

    decoded_string = ''.join(decoded_chars)
    return decoded_string, len(code)


def search_codec(encoding_name: str) -> Optional[codecs.CodecInfo]:
    if encoding_name != 'datamatrix.ascii':
        return None

    return codecs.CodecInfo(
        name='datamatrix.ascii',
        encode=encode,
        decode=decode
    )


codecs.register(search_codec)
