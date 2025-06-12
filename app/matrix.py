import importlib

from ecc import *


def encode_message(msg, codecs):
    encoded_candidates = []

    for codec in codecs:
        try:
            module = importlib.import_module(f"DataMatrix_PP.app.codec.codec_{codec.lower()}")
            encoded_result = module.encode(msg)

            if isinstance(encoded_result, tuple):
                encoded_result = encoded_result[0]

            if isinstance(encoded_result, bytes):
                encoded_result = list(encoded_result)
            elif isinstance(encoded_result, str):
                encoded_result = [ord(c) for c in encoded_result]
            elif isinstance(encoded_result, int):
                encoded_result = [encoded_result]

            encoded_candidates.append(encoded_result)
        except (ImportError, AttributeError, ValueError):
            continue

    return min(encoded_candidates, key=len)


def normalize_encoded_data(encoded_data):
    encoded_dict = {i: val for i, val in enumerate(encoded_data)}

    for i, val in encoded_dict.items():
        if isinstance(val, bytes):
            encoded_dict[i] = val[0] if len(val) == 1 else ord(str(val)[0])
        elif isinstance(val, str):
            encoded_dict[i] = ord(val)

    return encoded_dict


def calculate_layout_rectangular(data_length):
    sizes = [16, 7, 28, 11, 24, 14, 32, 18, 32, 24, 44, 28]
    layout_index = -1
    num_cols = 1

    while True:
        layout_index += 1
        width = sizes[layout_index]
        height = 6 + (layout_index & 12)
        block_capacity = width * height // 8

        layout_index += 1
        if block_capacity - sizes[layout_index] >= data_length:
            break

    if width > 25:
        num_cols = 2

    return width, height, layout_index, 1, num_cols


def calculate_layout_square(data_length):
    width = height = 6
    step = 2
    layout_index = -1
    sizes = [5, 7, 10, 12, 14, 18, 20, 24, 28, 36, 42, 48, 56, 68,
             84, 112, 144, 192, 224, 272, 336, 408, 496, 620]

    while True:
        layout_index += 1
        if layout_index == len(sizes):
            raise ValueError('Provided data is too long')

        if width > 11 * step:
            step = 4 + step & 12

        height += step
        width = height
        block_capacity = (width * height) >> 3

        if block_capacity - sizes[layout_index] >= data_length:
            break

    num_rows = num_cols = 1
    interleaved_blocks = 1

    if width > 27:
        num_rows = num_cols = 2 * (width // 54 | 0) + 2
    if block_capacity > 255:
        interleaved_blocks = 2 * (block_capacity >> 9) + 2

    return width, height, layout_index, interleaved_blocks, num_rows, num_cols


def add_padding(encoded_dict, data_length, block_capacity, ecc_codewords_total):
    if data_length < block_capacity - ecc_codewords_total:
        encoded_dict[data_length] = 129
        data_length += 1

    while data_length < block_capacity - ecc_codewords_total:
        encoded_dict[data_length] = (((149 * (data_length + 1)) % 253) + 130) % 254
        data_length += 1

    return data_length


def add_finder_patterns(matrix_map, width, height, num_rows, num_cols, module_width, module_height):
    def set_bit(x, y):
        matrix_map[y] = matrix_map.get(y, {})
        matrix_map[y][x] = 1

    for i in range(0, height + 2 * num_rows, module_height + 2):
        for j in range(0, width + 2 * num_cols):
            set_bit(j, i + module_height + 1)
            if (j & 1) == 0:
                set_bit(j, i)

    for i in range(0, width + 2 * num_cols, module_width + 2):
        for j in range(height):
            set_bit(i, j + (j // module_height | 0) * 2 + 1)
            if (j & 1) == 1:
                set_bit(i + module_width + 1, j + (j // module_height | 0) * 2)


def get_layout_coordinates(row, col, width, height, module_width, module_height):
    layout_pattern = [0, 0, -1, 0, -2, 0, 0, -1, -1, -1, -2, -1, -1, -2, -2, -2]

    if (row == height - 3 and col == -1):
        return [width, 6 - height, width, 5 - height, width, 4 - height, width, 3 - height,
                width - 1, 3 - height, 3, 2, 2, 2, 1, 2]
    elif row == height + 1 and col == 1 and (width & 7) == 0 and (height & 7) == 6:
        return [width - 2, -height, width - 3, -height, width - 4, -height,
                width - 2, -1 - height, width - 3, -1 - height, width - 4, -1 - height,
                width - 2, -2, -1, -2]
    elif row == height - 2 and col == 0 and (width & 3):
        return [width - 1, 3 - height, width - 1, 2 - height,
                width - 2, 2 - height, width - 3, 2 - height,
                width - 4, 2 - height, 0, 1, 0, 0, 0, -1]
    elif row == height - 2 and col == 0 and (width & 7) == 4:
        return [width - 1, 5 - height, width - 1, 4 - height, width - 1, 3 - height,
                width - 1, 2 - height, width - 2, 2 - height, 0, 1, 0, 0, 0, -1]
    else:
        return layout_pattern


def place_data_bits(matrix_map, encoded_dict, width, height, module_width, module_height, block_capacity):

    def set_bit(x, y):
        matrix_map[y] = matrix_map.get(y, {})
        matrix_map[y][x] = 1

    pattern_step = 2
    col = 0
    row = 4
    i = 0

    while i < block_capacity:
        if (row == height - 3 and col == -1):
            pass
        elif row == height + 1 and col == 1 and (width & 7) == 0 and (height & 7) == 6:
            pass
        else:
            if row == 0 and col == width - 2 and (width & 3):
                row -= pattern_step
                col += pattern_step
                continue
            if row < 0 or col >= width or row >= height or col < 0:
                pattern_step = -pattern_step
                row += 2 + pattern_step // 2
                col += 2 - pattern_step // 2
                while row < 0 or col >= width or row >= height or col < 0:
                    row -= pattern_step
                    col += pattern_step
            if row == 1 and col == width - 1 and (width & 7) == 0 and (height & 7) == 6:
                row -= pattern_step
                col += pattern_step
                continue

        layout_coords = get_layout_coordinates(row, col, width, height, module_width, module_height)
        value = encoded_dict[i]
        i += 1
        j = 0

        while value > 0:
            if value & 1:
                x = col + layout_coords[j]
                y = row + layout_coords[j + 1]

                if x < 0:
                    x += width
                    y += 4 - ((width + 4) & 7)
                if y < 0:
                    y += height
                    x += 4 - ((height + 4) & 7)

                set_bit(x + 2 * (x // module_width | 0) + 1,
                        y + 2 * (y // module_height | 0) + 1)

            j += 2
            value >>= 1

        row -= pattern_step
        col += pattern_step


def add_corner_pattern(matrix_map, width):

    def set_bit(x, y):
        matrix_map[y] = matrix_map.get(y, {})
        matrix_map[y][x] = 1

    i = width
    while i & 3:
        set_bit(i, i)
        i -= 1


def matrix_to_output(matrix_map, width, height, num_rows, num_cols):
    output_matrix = []
    total_rows = height + 2 * num_rows
    total_cols = width + 2 * num_cols

    for j in range(total_rows):
        output_matrix.append([])
        for i in range(total_cols):
            output_matrix[j].append(matrix_map[j].get(i, 0))

    return output_matrix


def matrix(msg, codecs, rectangular=False):
    encoded_data = encode_message(msg, codecs)
    encoded_dict = normalize_encoded_data(encoded_data)
    data_length = len(encoded_dict)

    if rectangular and data_length < 50:
        width, height, layout_index, interleaved_blocks, num_cols = calculate_layout_rectangular(data_length)
        num_rows = 1
        sizes = [16, 7, 28, 11, 24, 14, 32, 18, 32, 24, 44, 28]
    else:
        width, height, layout_index, interleaved_blocks, num_rows, num_cols = calculate_layout_square(data_length)
        sizes = [5, 7, 10, 12, 14, 18, 20, 24, 28, 36, 42, 48, 56, 68,
                 84, 112, 144, 192, 224, 272, 336, 408, 496, 620]

    ecc_codewords_total = sizes[layout_index]
    module_width = width // num_cols
    module_height = height // num_rows
    block_capacity = (width * height) >> 3

    data_length = add_padding(encoded_dict, data_length, block_capacity, ecc_codewords_total)

    ecc_codewords = ecc_codewords_total // interleaved_blocks
    antilog_table, log_table = generate_gf()
    rs_poly = generate_rs_poly(ecc_codewords, antilog_table, log_table)
    apply_rs_encoding(encoded_dict, data_length, interleaved_blocks, ecc_codewords, rs_poly, antilog_table, log_table)

    matrix_map = {}

    add_finder_patterns(matrix_map, width, height, num_rows, num_cols, module_width, module_height)

    place_data_bits(matrix_map, encoded_dict, width, height, module_width, module_height, block_capacity)

    add_corner_pattern(matrix_map, width)

    return matrix_to_output(matrix_map, width, height, num_rows, num_cols)