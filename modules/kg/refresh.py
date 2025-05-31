import time
import json
from Crypto.Cipher import AES
from common import scheduler
from common import config
from common import log
from .utils import signRequest, tools

logger = log.log("Refresh Login")

key = "90b8382a1bb4ccdcf063102053fd75b8"
iv = "f063102053fd75b8"

t1Key = "fd387891254e6cedc4019ca0061ea6d9"
t1Iv = "c4019ca0061ea6d9"

t2Key = "ce1e88d78dff2132dbfbb91af0ea9ca7"
t2Iv = "dbfbb91af0ea9ca7"


def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)


def unpad(s):
    return s[: -ord(s[len(s) - 1 :])]


def crypto_aes_encrypt(data: str | dict, key: str, iv: str):
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False)

    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    encrypted = cipher.encrypt(pad(data).encode("utf-8"))

    return encrypted.hex()


async def refresh_login_for_pool(user_info):
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
        "userid": userid,
        "clienttime_ms": timestamp,
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
        user_list = config.ReadConfig("module.kg.users")
        user_list[user_list.index(user_info)]["token"] = body["data"]["token"]
        user_list[user_list.index(user_info)]["userid"] = str(body["data"]["userid"])
        config.WriteConfig("module.kg.users", user_list)
        logger.info(f"为酷狗音乐账号(UID_{userid})数据更新完毕")


def reg_refresh_login_pool_task():
    user_info_pool = config.ReadConfig("module.kg.users")
    for user_info in user_info_pool:
        if user_info["refresh_login"]:
            scheduler.append(
                f'酷狗ck刷新: {user_info["userid"]}',
                refresh_login_for_pool,
                86400,
                args={"user_info": user_info},
            )


reg_refresh_login_pool_task()
