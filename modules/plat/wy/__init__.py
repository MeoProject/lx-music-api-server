from utils import orjson
from base64 import b64encode
from binascii import hexlify
from hashlib import md5
from Crypto.Cipher import AES

MODULUS: tuple[str] = (
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7"
    "b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280"
    "104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932"
    "575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b"
    "3ece0462db0a22b8e7"
)
PUBKEY: str = "010001"
NONCE: bytes = b"0CoJUm6Qyw8W8jud"
LINUXKEY: bytes = b"rFgB&h#%2?^eDg:Q"
EAPIKEY: bytes = b"e82ckenh8dichen8"
QMap: dict[dict, dict] = {
    "qualityMap": {
        "128k": "standard",
        "192k": "higher",
        "320k": "exhigh",
        "flac": "lossless",
        "hires": "hires",
        "atmos": "jyeffect",
        "master": "jymaster",
    },
    "qualityMapReverse": {
        "standard": "128k",
        "higher": "192k",
        "exhigh": "320k",
        "lossless": "flac",
        "hires": "hires",
        "jyeffect": "atmos",
        "jymaster": "master",
    },
}
EAPIKEY = b"e82ckenh8dichen8"


def MD5(value):
    m = md5()
    m.update(value.encode())
    return m.hexdigest()


def eEncrypt(url: str, data):
    data = orjson.dumps(data)
    text = str(data)
    digest = MD5("nobody{}use{}md5forencrypt".format(url, text))
    data = "{}-36cd479b6b5-{}-36cd479b6b5-{}".format(url, text, digest)
    return {"params": aes(data.encode(), EAPIKEY)}


def aes(text, key, method={}):
    pad = 16 - len(text) % 16
    text = text + bytearray([pad] * pad)
    if "iv" in method:
        encryptor = AES.new(key, AES.MODE_CBC, b"0102030405060708")
    else:
        encryptor = AES.new(key, AES.MODE_ECB)
    ciphertext = encryptor.encrypt(text)
    if "base64" in method:
        return b64encode(ciphertext)
    return (
        str(hexlify(ciphertext).upper())
        .replace(
            "b'",
            "",
        )
        .replace("'", "")
    )
