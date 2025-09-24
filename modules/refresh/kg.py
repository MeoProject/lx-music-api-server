import time
import ujson
import base64
from Crypto.Cipher import AES
from server.config import config
from utils.log import createLogger
from modules.plat.kg.utils import signRequest, tools

logger = createLogger("Refresh Login")

key = "90b8382a1bb4ccdcf063102053fd75b8"
iv = "f063102053fd75b8"


def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)


def unpad(s):
    return s[: -ord(s[len(s) - 1 :])]


def crypto_aes_encrypt(data: str | dict, key: str, iv: str):
    if isinstance(data, dict):
        data = ujson.dumps(data, ensure_ascii=False)

    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    encrypted = cipher.encrypt(pad(data).encode("utf-8"))

    return encrypted.hex()


async def refresh_login(user_info):
    userid = user_info["userid"]
    token = user_info["token"]

    if userid in ["", "0", 0]:
        return
    if token == "":
        return

    timestamp = int(time.time() * 1000)

    p3 = crypto_aes_encrypt({"clienttime": timestamp // 1000, "token": token}, key, iv)

    data = {
        "p3": p3,
        "plat": 1,
        "pk": "",
        "params": "",
        "t1": "",
        "userid": userid,
        "gitversion": "bab1274",
        "t2": "",
        "clienttime_ms": timestamp,
        "t3": "",
    }

    params = {
        "dfid": "-",
        "uuid": "-",
        "appid": tools[user_info["version"]]["appid"],
        "mid": tools["mid"],
        "clientver": tools[user_info["version"]]["clientver"],
        "clienttime": timestamp // 1000,
    }

    headers = {
        "User-Agent": "Android12-AndroidPhone-20149-201-0-ting#661004247|958959317-LOGIN-wifi",
        "X-Router": "login.user.kugou.com",
        "KG-THash": "25b8eea",
        "KG-Rec": "1",
        "KG-RC": "1",
    }

    req = await signRequest(
        "https://gateway.kugou.com/v5/login_by_token",
        params,
        {"method": "POST", "json": data, "headers": headers},
    )

    body = req.json()

    if body["error_code"] != 0:
        logger.warning(
            f'酷狗音乐账号(UID_{userid})刷新登录失败, code: {body["error_code"]}\n响应体: {body}'
        )
        return
    else:
        logger.info(f"酷狗音乐账号(UID_{userid})刷新登录成功")
        user_list = config.read("module.platform.kg.users")
        user_list[user_list.index(user_info)]["token"] = body["data"]["token"]
        user_list[user_list.index(user_info)]["userid"] = str(body["data"]["userid"])
        config.write("module.platform.kg.users", user_list)
        logger.info(f"为酷狗音乐账号(UID_{userid})数据更新完毕")
