import time
import traceback
from common import log
from common import config
from common import code
from common.utils import require
from common.variable import StatsManager
from common.exceptions import FailedException

from . import kw
from . import mg
from . import kg
from . import tx
from . import wy

logger = log.log("Music API Handler")
CACHE_ENABLE = config.ReadConfig("common.cache.enable")


sourceExpirationTime = {
    "tx": {
        "expire": True,
        "time": 80400,
    },
    "kg": {
        "expire": True,
        "time": 24 * 60 * 60,
    },
    "kw": {
        "expire": True,
        "time": 60 * 60,
    },
    "wy": {
        "expire": True,
        "time": 12 * 60,
    },
    "mg": {
        "expire": False,
        "time": 0,
    },
}


def contain_chinese(check_str: str):
    for ch in check_str:
        if "\u4e00" <= ch <= "\u9fa5":
            return True
    return False


async def url(source: str, songId: str, quality: str) -> dict:
    if quality == "flac24bit":
        quality = "hires"

    try:
        cache = config.GetCache("urls", f"{source}_{songId}_{quality}")
        if cache:
            cache = dict(cache)
            logger.info(
                f"使用缓存的{source}_{songId}_{quality}数据, URL: {cache['url']}"
            )
            StatsManager.increment(source, True)
            return {
                "code": code.SUCCESS,
                "message": "成功",
                "url": cache["url"],
                "info": cache["info"],
                "ekey": cache["ekey"],
                "cache": True,
                "quality": {
                    "target": quality,
                    "result": quality,
                },
                "expire": {
                    "ExpireAt": (
                        time.strftime(
                            "%Y-%m-%d %H:%M:%S", time.localtime(cache["time"])
                        )
                        if cache["expire"]
                        else None
                    ),
                    "canExpire": cache["expire"],
                },
            }
    except:
        StatsManager.increment(source, False)
        logger.error(traceback.format_exc())

    try:
        func = require("modules." + source + ".url")
    except:
        return {
            "code": code.NOT_FOUND,
            "message": "未知的源或不支持的方法",
        }

    try:
        result = dict(await func(songId, quality))
        logger.info(f"获取{source}_{songId}_{quality}成功, URL: {result['url']}")
        canExpire = sourceExpirationTime[source]["expire"]
        expireTime = int(sourceExpirationTime[source]["time"] * 0.75)
        expireAt = int(expireTime + time.time())

        if CACHE_ENABLE:
            config.UpdateCache(
                "urls",
                f"{source}_{songId}_{quality}",
                {
                    "expire": canExpire,
                    "time": expireAt,
                    "url": result["url"],
                    "ekey": result.get("ekey", ""),
                    "info": {
                        "id": songId,
                        "name": result.get("name", "无"),
                        "album": result.get("album", "无"),
                        "artist": result.get("artist", "无"),
                    },
                },
                expireTime if canExpire else None,
            )
            logger.info(
                f"缓存已更新: {source}_{songId}_{quality}, URL: {result['url']}, Expire: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expireAt))}"
            )

        StatsManager.increment(source, True)

        return {
            "code": code.SUCCESS,
            "message": "成功",
            "url": result["url"],
            "info": {
                "id": songId,
                "name": result.get("name", "无"),
                "album": result.get("album", "无"),
                "artist": result.get("artist", "无"),
            },
            "ekey": result.get("ekey", ""),
            "cache": False,
            "quality": {
                "target": quality,
                "result": result["quality"],
            },
            "expire": {
                "ExpireAt": (
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expireAt))
                    if canExpire
                    else None
                ),
                "canExpire": canExpire,
            },
        }
    except FailedException as e:
        StatsManager.increment(source, False)

        logger.error(f"获取{source}_{songId}_{quality}失败，原因：" + e.args[0])

        return {
            "code": code.SERVER_ERROR,
            "message": f"{e.args[0]}",
        }


async def lyric(source: str, songId: str, _) -> dict:
    cache = config.GetCache("lyric", f"{source}_{songId}")

    if cache and CACHE_ENABLE:
        return {
            "code": code.SUCCESS,
            "message": "成功",
            "info": f"{source}_{cache['info']}_{songId}",
            "lyric": cache["data"],
        }

    try:
        func = require("modules." + source + ".lyric")
    except:
        return {"code": code.NOT_FOUND, "message": "未知的源或不支持的方法"}

    try:
        result = await func(songId)
        expireTime = 86400 * 3
        expireAt = int(time.time() + expireTime)
        config.UpdateCache(
            "lyric",
            f"{source}_{songId}",
            {
                "data": result,
                "time": expireAt,
                "expire": True,
            },
            expireTime,
        )
        logger.debug(f"缓存已更新：{source}_{songId}, lyric: {result}")
        return {
            "code": code.SUCCESS,
            "message": "成功",
            "info": f"{source}_{songId}",
            "lyric": result,
        }
    except FailedException as e:
        logger.error(f"获取{source}_{songId}歌词失败，原因：" + e.args[0])
        return {
            "code": code.SERVER_ERROR,
            "message": e.args[0],
        }


async def search(source: str, songId: str, _) -> dict:
    try:
        func = require("modules." + source + ".search")
    except:
        return {"code": code.NOT_FOUND, "message": "未知的源或不支持的方法"}

    try:
        result = await func(songId)
        return {"code": code.SUCCESS, "message": "成功", "result": result}
    except FailedException as e:
        return {"code": code.FAILED, "message": e.args[0]}
