import base64


def createBase64Encode(data_bytes):
    encoded_data = base64.b64encode(data_bytes)
    return encoded_data.decode("utf-8")


def createBase64Decode(data):
    decoded_data = base64.b64decode(data)
    return decoded_data
