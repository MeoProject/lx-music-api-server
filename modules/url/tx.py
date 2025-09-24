import random
from urllib.parse import urlencode
from server.config import config
from server.exceptions import getUrlFailed
from modules.plat.tx import build_common_params, utils
from modules.info.tx import getMusicInfo
from server.models import UrlResponse

translate = {
    0: "无版权/未知原因",
    1000: "未登录",
    104003: "请求不合法/无版权/Q音账号被封禁/服务器IP被封禁",
}


async def getUrl(songId: str | int, quality: str) -> UrlResponse:
    if config.read("module.qmc_decrypter"):
        try:
            result = await getEncryptedUrl(songId, quality)
            params = {"url": result.url, "ekey": result.ekey}
            url = f"http://{config.read('server.link')}/qmc/decrypt?" + urlencode(
                params
            )
            return UrlResponse(url, quality, result.ekey)
        except Exception as e:
            raise e
    else:
        try:
            result = await getUnencryptedUrl(songId, quality)
            return result
        except Exception as e:
            raise e


async def getUnencryptedUrl(songId: str | int, quality: str) -> UrlResponse:
    try:
        info = await getMusicInfo(songId)
    except:
        raise getUrlFailed("详情获取失败")

    songId = info.songMid
    strMediaMid = info.mediaMid

    user_info = config.read("module.platform.tx.users")

    if quality not in ["128k", "320k", "flac", "hires"]:
        user_info = random.choice(
            [user for user in user_info if user.get("vip_type") == "svip"]
        )
    else:
        user_info = random.choice(user_info)

    requestBody = {
        "request": {
            "module": "music.vkey.GetVkey",
            "method": "UrlGetVkey",
            "param": {
                "guid": "musicapi",
                "uin": user_info["uin"],
                "downloadfrom": 1,
                "ctx": 1,
                "referer": "y.qq.com",
                "scene": 0,
                "songtype": [1],
                "songmid": [songId],
                "filename": [
                    f'{utils.Tools["File"]["fileInfo"][quality]["h"]}{strMediaMid}{utils.Tools["File"]["fileInfo"][quality]["e"]}'
                ],
            },
        },
    }

    requestBody["comm"] = await build_common_params(user_info)

    req = await utils.signRequest(requestBody)
    body = req.json()
    data = body["request"]["data"]["midurlinfo"][0]

    purl = str(data["purl"])

    if not purl:
        raise getUrlFailed(translate[body["request"]["code"]])

    url = UrlResponse(url=utils.Tools["cdnaddr"] + purl, quality=quality, ekey="")

    return url


async def getEncryptedUrl(songId: str | int, quality: str) -> UrlResponse:
    try:
        info = await getMusicInfo(songId)
    except:
        raise getUrlFailed("详情获取失败")

    songId = info.songMid
    strMediaMid = info.mediaMid

    user_info = config.read("module.platform.tx.users")

    if quality not in ["128k", "320k", "flac", "hires"]:
        user_info = random.choice(
            [user for user in user_info if user.get("vip_type") == "svip"]
        )
    else:
        user_info = random.choice(user_info)

    requestBody = {
        "request": {
            "module": "music.vkey.GetEVkey",
            "method": "CgiGetEVkey",
            "param": {
                "guid": "musicapi",
                "uin": user_info["uin"],
                "downloadfrom": 1,
                "ctx": 1,
                "referer": "y.qq.com",
                "scene": 0,
                "songtype": [1],
                "songmid": [songId],
                "filename": [
                    f'{utils.Tools["EncryptFile"]["fileInfo"][quality]["h"]}{strMediaMid}{utils.Tools["EncryptFile"]["fileInfo"][quality]["e"]}'
                ],
            },
        },
    }

    requestBody["comm"] = await build_common_params(user_info)

    req = await utils.signRequest(requestBody)
    body = req.json()
    data = body["request"]["data"]["midurlinfo"][0]

    purl = str(data["purl"])
    ekey = str(data["ekey"])

    if not purl:
        raise getUrlFailed(translate[body["request"]["code"]])

    url = UrlResponse(url=utils.Tools["cdnaddr"] + purl, quality=quality, ekey=ekey)

    return url
