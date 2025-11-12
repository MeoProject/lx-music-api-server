import time
import base64
import hashlib
from utils import orjson
from utils.log import createLogger
from server.config import config
from modules.plat.kg.utils import signRequest, tools

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

logger = createLogger("Refresh Login")

PUBLIC_KEY = RSA.import_key(
    base64.b64decode(
        "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIAG7QOELSYoIJvTFJhMpe1s/gbjDJX51HBNnEl5HXqTW6lQ7LC8jr9fWZTwusknp+sVGzwd40MwP6U5yDE27M/X1+UR4tvOGOqp94TJtQ1EPnWGWXngpeIW5GxoQGao1rmYWAu6oi1z9XkChrsUdC6DJE5E221wf/4WLFxwAtRQIDAQAB"
    )
)


def calcHash(input_str: str) -> str:
    md5 = hashlib.md5()
    md5.update(input_str.encode("utf-8"))
    return md5.hexdigest()


def randomString(length: int) -> str:
    import string
    import random

    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def cryptoAesEncrypt(data: str | dict, key: str = None, iv: str = None) -> dict | str:
    if isinstance(data, dict):
        data = orjson.dumps(data)

    if key is None:
        temp_key = randomString(16).lower()
        key = calcHash(temp_key)[:32]
        iv = key[16:32]
        return_key = True
    else:
        temp_key = None
        return_key = False
        if iv is None:
            processed_key = calcHash(key)
            key = processed_key[:32]
            iv = key[16:32]

    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    encrypted = cipher.encrypt(pad(data.encode("utf-8"), AES.block_size))
    hex_str = encrypted.hex()

    if return_key:
        return {"str": hex_str, "key": temp_key}
    else:
        return hex_str


def cryptoAesDecrypt(data: str, key: str, iv: str = None) -> dict | str:
    if iv is None:
        processed_key = calcHash(key)
        key = processed_key[:32]
        iv = key[16:32]

    encrypted_bytes = bytes.fromhex(data)

    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    decrypted = cipher.decrypt(encrypted_bytes)
    decrypted = unpad(decrypted, AES.block_size)

    try:
        result_str = decrypted.decode("utf-8")
        try:
            return orjson.loads(result_str)
        except:
            return result_str
    except:
        return decrypted


def cryptoRSAEncrypt(data: dict | str) -> str:
    if isinstance(data, dict):
        data = orjson.dumps(data)

    data_bytes = data.encode("utf-8")

    if len(data_bytes) > 128:
        padded_data = data_bytes[:128]
    else:
        padded_data = data_bytes + bytes(128 - len(data_bytes))

    m = int.from_bytes(padded_data, byteorder="big")
    c = pow(m, PUBLIC_KEY.e, PUBLIC_KEY.n)
    encrypted = c.to_bytes(128, byteorder="big")

    return encrypted.hex()


async def refreshLogin(user_info):
    userid = user_info["userid"]
    token = user_info["token"]

    if userid in ["", "0", 0]:
        return
    if token == "":
        return

    clienttime = int(time.time())
    clienttime_ms = int(clienttime * 1000)

    p3 = cryptoAesEncrypt(
        {"clienttime": clienttime, "token": token},
        key="90b8382a1bb4ccdcf063102053fd75b8",
        iv="f063102053fd75b8",
    )

    encryptParams = cryptoAesEncrypt({})

    pk = cryptoRSAEncrypt(
        {
            "clienttime_ms": clienttime_ms,
            "key": encryptParams["key"],
        }
    )

    req = await signRequest(
        "http://gateway.kugou.com/v5/login_by_token",
        {
            "dfid": "-",
            "uuid": "-",
            "appid": "1005",
            "mid": tools["mid"],
            "clientver": "20349",
            "clienttime": clienttime,
        },
        {
            "method": "POST",
            "body": {
                "p3": p3,
                "params": encryptParams["str"],
                "userid": userid,
                "need_toneinfo": 1,
                "clienttime_ms": clienttime_ms,
                "dfid": "-",
                "dev": "SDY-AN00",
                "plat": 1,
                "pk": pk,
                "t1": "0",
                "gitversion": "a23c277",
                "t2": "0",
                "t3": "MCwwLDEsMSwwLDYsMSw2LDA=",
            },
            "headers": {
                "SUPPORT-CALM": "1",
                "KG-THash": "6a6a1ba",
                "x-router": "login.user.kugou.com",
                "User-Agent": "Android12-AndroidPhone-20349-201-0-ting#958959317/661004247-LOGIN-wifi",
                "KG-RC": "1",
            },
        },
    )

    body = req.json()

    if body["error_code"] != 0:
        logger.warning(
            f"酷狗音乐账号(UID_{userid})刷新登录失败, code: {body['error_code']}\n响应体: {body}"
        )
        return
    else:
        logger.info(f"酷狗音乐账号(UID_{userid})刷新登录成功")

        decrypted_token = cryptoAesDecrypt(
            body["data"]["secu_params"],
            encryptParams["key"],
        )

        user_list = config.read("modules.platform.kg.users")
        user_list[user_list.index(user_info)]["token"] = decrypted_token["token"]

        config.write("modules.platform.kg.users", user_list)
        logger.info(f"为酷狗音乐账号(UID_{userid})数据更新完毕")
