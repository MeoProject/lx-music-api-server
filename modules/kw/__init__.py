import random
from common import request, log
from common.config import ReadConfig
from common.exceptions import FailedException
from .des import createEncrypt, createDecrypt

logger = log.log("KWMusic")

tools = {
    "qualityMap": {
        "128k": "128kmp3",
        "192k": "192kogg",
        "320k": "320kmp3",
        "flac": "2000kflac",
        "hires": "4000kflac",
        "atmos": "20201kmflac",
        "atmos_plus": "20501kmflac",
        "master": "20900kmflac",
    },
    "qualityMapReverse": {
        99: "99k",
        100: "100k",
        128: "128k",
        256: "256k",
        320: "320k",
        2000: "flac",
        4000: "hires",
        20201: "atmos",
        20501: "atmos_plus",
        20900: "master",
    },
    "extMap": {
        "128k": "mp3",
        "320k": "mp3",
        "flac": "flac",
        "hires": "flac",
        "atmos": "mflac",
        "atmos_plus": "mflac",
        "master": "mflac",
    },
}


async def url(songId, quality):
    source_config = dict(random.choice(ReadConfig("module.kw.source_config_list")))

    params = source_config["params"].copy()

    for key, value in params.items():
        if isinstance(value, str):
            params[key] = (
                value.replace("{songId}", songId)
                .replace("{mapQuality}", tools["qualityMap"][quality])
                .replace("{ext}", tools["extMap"][quality])
            )

    params["source"] = source_config["source"]

    rawParams = "&".join([f"{k}={v}" for k, v in params.items()])

    if source_config["isenc"]:
        rawParams = createEncrypt(rawParams)

    target_url = f'https://{source_config["type"]}.kuwo.cn/mobi.s?{rawParams}'

    req = await request.AsyncRequest(
        target_url,
        {
            "method": "GET",
            "headers": {"User-Agent": "okhttp/3.10.0"},
        },
    )

    if req.json()["code"] != 200:
        raise FailedException("失败")

    body = dict(req.json().get("data", {}))

    url = str(body.get("surl", body.get("url", "")))
    bitrate = int(body.get("bitrate", 1))

    if url == "" or bitrate == 1 or bitrate not in tools["qualityMapReverse"]:
        raise FailedException("失败")

    if tools["qualityMapReverse"][bitrate] != quality:
        logger.info(
            f"酷我音乐 {songId}, {quality} -> {tools['qualityMapReverse'][bitrate]}"
        )

    if body["format"] == "mflac":
        ekey = createDecrypt(req.json()["data"]["ekey"])
    else:
        ekey = None

    info_url = f"http://musicpay.kuwo.cn/music.pay?ver=MUSIC_9.1.1.2_BCS2&src=mbox&op=query&signver=new&action=play&ids={songId}&accttype=1&appuid=38668888"
    info_req = await request.AsyncRequest(info_url)
    info_body = info_req.json()

    return {
        "name": info_body["songs"][0]["name"],
        "artist": info_body["songs"][0]["artist"],
        "album": info_body["songs"][0]["album"],
        "url": url.split("?")[0],
        "quality": tools["qualityMapReverse"][bitrate],
        "ekey": ekey,
    }
