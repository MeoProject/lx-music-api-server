from typing import Any


Translates = {
    "kw": "酷我音乐",
    "tx": "QQ音乐",
    "kg": "酷狗音乐",
    "wy": "网易云音乐",
    "mg": "咪咕音乐",
    "128k": "标准音质 128K",
    "320k": "高品音质 320K",
    "flac": "无损音质 FLAC",
    "hires": "无损音质 24Bit",
    "master": "臻品母带",
    "viper_clear": "蝰蛇超清",
    "viper_atmos": "蝰蛇全景声",
    "dolby": "杜比全景声",
    "atmos": "臻品全景声",
    "atmos_plus": "臻品全景声2.0",
    3: "链接获取失败, 无版权",
    2: "链接获取失败, 数字专辑",
    1: "链接获取失败, 数字专辑/API失效",
    0: "未知原因，大概率是无版权(Q音多发)",
    1000: "Token已过期/无版权",
    104003: "请求不合法/无版权/Q音账号被封禁/服务器IP被封禁",
}


def translateStrOrInt(word: str | int) -> Any:
    try:
        result = Translates[word]
        return result
    except:
        return "Translate Error"


def getExpireTime(source: str) -> int:
    if source == "tx":
        return 80400
    elif source == "kg":
        return 24 * 60 * 60
    elif source == "kw":
        return 60 * 60
    elif source == "wy":
        return 12 * 60
    else:
        return 0
