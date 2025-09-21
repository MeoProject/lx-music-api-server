import binascii


def createHexEncode(data_bytes):
    hex_encoded = binascii.hexlify(data_bytes)
    return hex_encoded.decode("utf-8")


def createHexDecode(data):
    decoded_data = binascii.unhexlify(data.decode("utf-8"))
    return decoded_data
