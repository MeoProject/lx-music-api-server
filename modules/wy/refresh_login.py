# ----------------------------------------
# - mode: python -
# - author: lerdb -
# - name: refresh_login.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common import Httpx, variable
from common import scheduler
from common import config
from common import log
from common.exceptions import FailedException
from time import time
from random import randint
from .encrypt import eapiEncrypt
import ujson as json

logger = log.log("wy_refresh_login")


def cookieStr2Dict(cookieStr):
    cookieDict = {}
    for line in cookieStr.split(";"):
        if line.strip() == "":
            continue
        try:
            name, value = line.strip().split("=", 1)
            cookieDict[name] = value
        except:
            continue
    return cookieDict


def cookieDict2Str(cookieDict):
    cookieStr = ""
    for name, value in cookieDict.items():
        cookieStr += f"{name}={value}; "
    return cookieStr


async def refresh(cookie:str):
    """
    网易云刷新登录
    
    @param cookie: 网易云音乐cookie
    """
    cookie = cookieStr2Dict(cookie)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
    }
    baseUrl = "http://interface.music.163.com/eapi/"
    path = "/api/login/token/refresh"
    header = {
        "osver": cookie.get("osver", "17.4.1"),
        "deviceId": cookie.get("deviceId",""),
        "os": cookie.get("os","ios"),
        "appver": cookie.get("appver", ("9.0.65" if cookie.get("os") != "pc" else "")),
        "versioncode": cookie.get("versioncode", "140"),
        "mobilename": cookie.get("mobilename", ""),
        "buildver": cookie.get("buildver", str(time())[:10]),
        "resolution": cookie.get("resolution", "1920x1080"),
        "__csrf": cookie.get("__csrf", ""),
        "channel": cookie.get("channel", ""),
        "requestId": str(time() * 1000)[:13] + "_" + f"{randint(0, 9999):0>4}",
    }
    if cookie.get("MUSIC_U"):
        header["MUSIC_U"] = cookie.get("MUSIC_U")
    if cookie.get("MUSIC_A"):
        header["MUSIC_A"] = cookie.get("MUSIC_A")
    headers["Cookie"] = cookieDict2Str(header)

    req = await Httpx.AsyncRequest(
        baseUrl + path[5:],
        {
            "method": "POST",
            "headers": headers,
            "form": eapiEncrypt(path, json.dumps({"header": header, "e_r": False})),
        }
    )
    body = req.json()
    if int(body["code"]) != 200:
        raise FailedException("网易云刷新登录失败(code: " + body["code"] + ")")
    return logger.info("网易云刷新登录成功")

if (variable.use_cookie_pool):
    cookies = config.read_config("module.cookiepool.wy")
    for c in cookies:
        ref = c.get("refresh_login") if c.get("refresh_login") else {
            "enable": False,
            "interval": 86400
        }
        if (ref["enable"]):
            scheduler.append("wy_refresh_login_pooled_" + c["cookie"][:32], refresh, ref["interval"], {"cookie": c["cookie"]})
else:
    c = config.read_config("module.wy.user.cookie")
    ref = config.read_config("module.wy.user.refresh_login")
    if (ref["enable"]):
        scheduler.append("wy_refresh_login", refresh, ref["interval"], {"cookie": c})