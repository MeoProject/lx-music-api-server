import random
from .detail import getMusicInfo
from .utils import signRequest, tools, formatSinger
from common import config
from common.exceptions import FailedException


async def url(songId: str, quality: str, try_cishu: int = 0):
    if try_cishu > 3:
        raise FailedException(f"获取失败")

    enc = False

    if "_e" in songId:
        enc = True

    infoBody = await getMusicInfo(songId)
    songId = infoBody["track_info"]["mid"]
    strMediaMid = infoBody["track_info"]["file"]["media_mid"]
    user_info = config.ReadConfig("module.tx.users")

    if quality == "master":
        user_info = random.choice(
            [user for user in user_info if user.get("vip_type") == "svip"]
        )
    else:
        user_info = random.choice(user_info)

    requestBody = {
        "comm": {
            "ct": "11",
            "cv": "12050505",
            "v": "12050505",
            "chid": "2005000894",
            "tmeLoginMethod": "2",
            "tmeLoginType": "2",
            "OpenUDID2": user_info["devices"]["UDID2"],
            "QIMEI36": user_info["devices"]["QIMEI"],
            "tmeAppID": "qqmusic",
            "rom": user_info["devices"]["fingerprint"],
            "fPersonality": "0",
            "OpenUDID": user_info["devices"]["UDID"],
            "udid": user_info["devices"]["UDID"],
            "os_ver": user_info["devices"]["osver"],
            "aid": user_info["devices"]["aid"],
            "phonetype": user_info["devices"]["model"],
            "devicelevel": user_info["devices"]["level"],
            "newdevicelevel": user_info["devices"]["level"],
            "qq": user_info["uin"],
            "authst": user_info["token"],
        },
        "request": {
            "module": "music.vkey.GetVkey",
            "method": "UrlGetVkey",
            "param": {
                "uin": user_info["uin"],
                "guid": user_info["devices"]["UDID2"],
                "songmid": [songId],
                "songtype": [1],
                "filename": [
                    (
                        f'{tools["File"]["fileInfo"][quality]["h"]}{strMediaMid}{tools["File"]["fileInfo"][quality]["e"]}'
                        if not enc
                        else f'{tools["encryptFile"]["fileInfo"][quality]["h"]}{strMediaMid}{tools["File"]["fileInfo"][quality]["e"]}'
                    )
                ],
                "downloadfrom": 0,
                "ctx": 1,
            },
        },
    }

    try:
        req = await signRequest(requestBody)
        body = req.json()
        data = body["request"]["data"]["midurlinfo"][0]
        purl = data["purl"]

        if enc:
            ekey = data["ekey"]
        else:
            ekey = None

        if not purl:
            try_cishu += 1
            return await url(songId, quality, try_cishu)

        purl = (
            (purl + f"&fromtag={random.randint(1, 99999)}")
            if not "fromtag" in purl
            else purl
        )

        return {
            "name": infoBody["track_info"]["title"],
            "artist": formatSinger(infoBody["track_info"]["singer"]),
            "album": infoBody["track_info"]["album"]["title"],
            "url": tools["cdnaddr"] + purl,
            "quality": quality,
            "ekey": ekey,
        }
    except Exception as e:
        raise FailedException(f"获取失败：{e}")
