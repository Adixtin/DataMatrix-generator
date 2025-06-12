def generate_gf():
    antilog_table = [0] * 255
    log_table = [0] * 256
    value = 1
    for i in range(255):
        antilog_table[i] = value
        log_table[value] = i
        value <<= 1
        if value > 255:
            value ^= 301  # 0x12D, primitive polynomial for GF(256)
    return antilog_table, log_table


def generate_rs_poly(ecc_codewords, antilog_table, log_table):
    reed_solomon = [0] * (ecc_codewords + 1)
    reed_solomon[ecc_codewords] = 0
    for i in range(1, ecc_codewords + 1):
        reed_solomon[ecc_codewords - i] = 1
        for j in range(ecc_codewords - i, ecc_codewords):
            reed_solomon[j] = reed_solomon[j + 1] ^ antilog_table[(log_table[reed_solomon[j]] + i) % 255]
    return reed_solomon


def apply_rs_encoding(enc, msg_len, blocks, ecc_codewords, reed_solomon, antilog_table, log_table):
    remainder = [0] * 70
    for c in range(blocks):
        for i in range(ecc_codewords + 1):
            remainder[i] = 0
        for i in range(c, msg_len, blocks):
            x = remainder[0] ^ enc[i]
            for j in range(ecc_codewords):
                if x:
                    remainder[j] = remainder[j + 1] ^ antilog_table[(log_table[reed_solomon[j]] + log_table[x]) % 255]
                else:
                    remainder[j] = remainder[j + 1]
        for i in range(ecc_codewords):
            enc[msg_len + c + i * blocks] = remainder[i]
