import base64
import logging
import random
from datetime import datetime, timedelta
from time import time
from typing import TypedDict, cast

from utils import orjson
from . import http
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .md5 import createMD5
from .device import Device, get_cached_device, save_device

logger = logging.getLogger("qqmusicapi.qimei")

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDEIxgwoutfwoJxcGQeedgP7FG9qaIuS0qzfR8gWkrkTZKM2iWHn2ajQpBRZjMSoSf6+KJGvar2ORhBfpDXyVtZCKpqLQ+FLkpncClKVIrBwv6PHyUvuCb0rIarmgDnzkfQAqVufEtR64iazGDKatvJ9y6B9NMbHddGSAUmRTCrHQIDAQAB
-----END PUBLIC KEY-----"""
SECRET = "ZdJqM15EeO2zWc08"
APP_KEY = "0AND0HD6FE4HY80F"


class QimeiResult(TypedDict):
    """获取 QIMEI 结果"""

    q16: str
    q36: str


def rsa_encrypt(content: bytes) -> bytes:
    """RSA 加密"""
    key = cast(RSAPublicKey, serialization.load_pem_public_key(PUBLIC_KEY.encode()))
    return key.encrypt(content, padding.PKCS1v15())


def aes_encrypt(key: bytes, content: bytes) -> bytes:
    """AES-CBC 加密数据"""
    cipher = Cipher(algorithms.AES(key), modes.CBC(key))
    padding_size = 16 - len(content) % 16
    encryptor = cipher.encryptor()
    return (
        encryptor.update(content + (padding_size * chr(padding_size)).encode())
        + encryptor.finalize()
    )


def random_beacon_id() -> str:
    """随机 BeaconID"""
    beacon_id = ""
    time_month = datetime.now().strftime("%Y-%m-") + "01"
    rand1 = random.randint(100000, 999999)
    rand2 = random.randint(100000000, 999999999)

    for i in range(1, 41):
        if i in [1, 2, 13, 14, 17, 18, 21, 22, 25, 26, 29, 30, 33, 34, 37, 38]:
            beacon_id += f"k{i}:{time_month}{rand1}.{rand2}"
        elif i == 3:
            beacon_id += "k3:0000000000000000"
        elif i == 4:
            beacon_id += f"k4:{''.join(random.choices('123456789abcdef', k=16))}"
        else:
            beacon_id += f"k{i}:{random.randint(0, 9999)}"
        beacon_id += ";"
    return beacon_id


def random_payload_by_device(device: Device, version: str) -> dict:
    """随机 payload"""
    fixed_rand = random.randint(0, 14400)
    reserved = {
        "harmony": "0",
        "clone": "0",
        "containe": "",
        "oz": "UhYmelwouA+V2nPWbOvLTgN2/m8jwGB+yUB5v9tysQg=",
        "oo": "Xecjt+9S1+f8Pz2VLSxgpw==",
        "kelong": "0",
        "uptimes": (datetime.now() - timedelta(seconds=fixed_rand)).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "multiUser": "0",
        "bod": device.brand,
        "dv": device.device,
        "firstLevel": "",
        "manufact": device.brand,
        "name": device.model,
        "host": "se.infra",
        "kernel": device.proc_version,
    }
    return {
        "androidId": device.android_id,
        "platformId": 1,
        "appKey": APP_KEY,
        "appVersion": version,
        "beaconIdSrc": random_beacon_id(),
        "brand": device.brand,
        "channelId": "10003505",
        "cid": "",
        "imei": device.imei,
        "imsi": "",
        "mac": "",
        "model": device.model,
        "networkType": "unknown",
        "oaid": "",
        "osVersion": f"Android {device.version.release},level {device.version.sdk}",
        "qimei": "",
        "qimei36": "",
        "sdkVersion": "1.2.13.6",
        "targetSdkVersion": "33",
        "audit": "",
        "userId": "{}",
        "packageId": "com.tencent.qqmusic",
        "deviceType": "Phone",
        "sdkName": "",
        "reserved": orjson.dumps(reserved),
    }


async def get_qimei(version: str) -> QimeiResult:
    """获取 QIMEI"""
    device = get_cached_device()
    try:
        payload = random_payload_by_device(device, version)
        crypt_key = "".join(random.choices("adbcdef1234567890", k=16))
        nonce = "".join(random.choices("adbcdef1234567890", k=16))
        ts = int(time())
        key = base64.b64encode(rsa_encrypt(crypt_key.encode())).decode()
        params = base64.b64encode(
            aes_encrypt(crypt_key.encode(), orjson.dumps(payload).encode())
        ).decode()
        extra = '{"appKey":"' + APP_KEY + '"}'
        sign = createMD5(key, params, str(ts * 1000), nonce, SECRET, extra)
        res = await http.HttpRequest(
            "https://api.tencentmusic.com/tme/trpc/proxy",
            {
                "method": "POST",
                "headers": {
                    "Host": "api.tencentmusic.com",
                    "method": "GetQimei",
                    "service": "trpc.tme_datasvr.qimeiproxy.QimeiProxy",
                    "appid": "qimei_qq_android",
                    "sign": createMD5(
                        "qimei_qq_androidpzAuCmaFAaFaHrdakPjLIEqKrGnSOOvH", str(ts)
                    ),
                    "User-Agent": "QQMusic",
                    "timestamp": str(ts),
                },
                "data": {
                    "app": 0,
                    "os": 1,
                    "qimeiParams": {
                        "key": key,
                        "params": params,
                        "time": str(ts),
                        "nonce": nonce,
                        "sign": sign,
                        "extra": extra,
                    },
                },
            },
        )
        logger.debug("获取 QIMEI 成功: %s", res.json())
        data = orjson.loads(orjson.loads(res.content)["data"])["data"]
        device.qimei = data
        save_device(device)
        return QimeiResult(q16=data["q16"], q36=data["q36"])
    except:
        if device.qimei:
            return QimeiResult(q16="", q36=device.qimei)
        logger.error("获取 QIMEI 失败,使用默认 QIMEI")
        return QimeiResult(q16="", q36="6c9d3cd110abca9b16311cee10001e717614")
