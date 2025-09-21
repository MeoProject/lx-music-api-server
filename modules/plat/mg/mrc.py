# From lyswhut/lx-music-desktop
DELTA = 2654435769
MIN_LENGTH = 32
KEY_ARR = [
    27303562373562475,
    18014862372307051,
    22799692160172081,
    34058940340699235,
    30962724186095721,
    27303523720101991,
    27303523720101998,
    31244139033526382,
    28992395054481524,
]
MAX_LONG = 9223372036854775807
MIN_LONG = -9223372036854775808


def to_long(value):
    if isinstance(value, str):
        num = int(value, 16)
    else:
        num = int(value)

    while num > MAX_LONG:
        num = num - (1 << 64)
    while num < MIN_LONG:
        num = num + (1 << 64)

    return num


def long_to_bytes(value):
    result = bytearray(8)
    value = int(value)

    for i in range(8):
        result[i] = value & 0xFF
        value >>= 8

    return bytes(result)


def long_arr_to_string(data):
    result_parts = []
    for j in data:
        byte_data = long_to_bytes(j)
        try:
            text = byte_data.decode("utf-16le")
            result_parts.append(text)
        except UnicodeDecodeError:
            continue

    return "".join(result_parts)


def to_bigint_array(data: str):
    length = len(data) // 16
    result = []

    for i in range(length):
        hex_str = data[i * 16 : (i + 1) * 16]
        result.append(to_long(hex_str))

    return result


def tea_decrypt(data, key):
    length = len(data)

    if length >= 1:
        j2 = data[0]
        j3 = to_long((6 + 52 // length) * DELTA)

        while True:
            j4 = j3
            if j4 == 0:
                break

            j5 = to_long(3 & to_long(j4 >> 2))
            j6 = length

            while True:
                j6 -= 1
                if j6 > 0:
                    j7 = data[j6 - 1]
                    i = j6

                    temp1 = to_long(j2 ^ j4)
                    temp2 = to_long(j7 ^ key[to_long((3 & j6) ^ j5)])
                    temp3 = to_long(temp1 + temp2)

                    temp4 = to_long(j7 >> 5) ^ to_long(j2 << 2)
                    temp5 = to_long(j2 >> 3) ^ to_long(j7 << 4)
                    temp6 = to_long(temp4 + temp5)

                    temp7 = to_long(temp3 ^ temp6)
                    j2 = to_long(data[i] - temp7)
                    data[i] = j2
                else:
                    break

            j8 = data[length - 1]

            temp1 = to_long(key[to_long((j6 & 3) ^ j5)] ^ j8)
            temp2 = to_long(j2 ^ j4)
            temp3 = to_long(temp1 + temp2)

            temp4 = to_long(j8 >> 5) ^ to_long(j2 << 2)
            temp5 = to_long(j2 >> 3) ^ to_long(j8 << 4)
            temp6 = to_long(temp4 + temp5)

            temp7 = to_long(temp3 ^ temp6)
            j2 = to_long(data[0] - temp7)
            data[0] = j2

            j3 = to_long(j4 - DELTA)

    return data


def decrypt(data: str) -> str:
    if data is None or len(data) < MIN_LENGTH:
        return data
    try:
        bigint_array = to_bigint_array(data)
        decrypted_array = tea_decrypt(bigint_array.copy(), KEY_ARR)
        result = long_arr_to_string(decrypted_array)
        return result
    except Exception:
        return data
