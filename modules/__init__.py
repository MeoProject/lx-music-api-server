import time

from utils import log
from .constants import (
    getExpireTime,
    translateStrOrInt,
)
from server.config import config, cache as cacheM
from server.models import Song, SongInfo, UrlResponse
from server.exceptions import getLyricFailed, getSongInfoFailed, getUrlFailed

from . import plat
from . import refresh
from . import url
from . import lyric
from . import info

logger = log.createLogger("Music API Handler")
CACHE_ENABLE = config.read("cache.enable")


def require(module: str):
    index = 0
    module_array = module.split(".")
    for m in module_array:
        if index == 0:
            _module = __import__(m)
            index += 1
        else:
            _module = getattr(_module, m)
            index += 1
    return _module


async def getUrlForAPI(source: str, songId: str, quality: str) -> dict:
    if quality == "flac24bit":
        quality = "hires"

    if CACHE_ENABLE:
        try:
            cache = cacheM.get("urls", f"{source}_{songId}_{quality}")
            if cache:
                cache = dict(cache)
                result = UrlResponse(**cache["url"])
                logger.info(
                    "使用缓存的%s_%s_%s数据, URL: %s" % translateStrOrInt(source),
                    songId,
                    translateStrOrInt(result.quality),
                    result.url,
                )
                return {
                    "code": 200,
                    "message": "成功",
                    "url": result.url,
                    "ekey": result.ekey,
                    "quality": translateStrOrInt(result.quality),
                    "cache": {
                        "cache": True,
                        "canExpire": cache["expire"],
                        "expireAt": (
                            time.strftime(
                                "%Y-%m-%d %H:%M:%S", time.localtime(cache["time"])
                            )
                            if cache["expire"]
                            else None
                        ),
                    },
                }
        except:
            pass

    try:
        func = require(f"modules.url.{source}.getUrl")
    except:
        return {
            "code": 404,
            "message": "未知的源或不支持的方法",
        }

    try:
        result: UrlResponse | Song = await func(songId, quality)
        if source == "mg":
            result: UrlResponse = result.url

        logger.info(
            "获取%s_%s_%s成功, URL: %s"
            % (
                translateStrOrInt(source),
                songId,
                translateStrOrInt(quality),
                result.url,
            )
        )
        expireTime = getExpireTime(source)
        expireTime, canExpire = (
            int(expireTime * 0.75),
            True if expireTime != 0 else False,
        )
        expireAt = int(expireTime + time.time())
        if CACHE_ENABLE:
            cacheM.set(
                "urls",
                f"{source}_{songId}_{quality}",
                {
                    "time": expireAt,
                    "expire": canExpire,
                    "url": result.__dict__,
                },
                expireTime if canExpire else None,
            )
            logger.info(
                "缓存已更新: %s_%s_%s, URL: %s, Expire: %s"
                % (
                    translateStrOrInt(source),
                    songId,
                    translateStrOrInt(quality),
                    result.url,
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expireAt)),
                )
            )

        return {
            "code": 200,
            "message": "成功",
            "url": result.url,
            "ekey": result.ekey,
            "quality": translateStrOrInt(result.quality),
            "cache": {
                "cache": False,
                "canExpire": canExpire,
                "expireAt": (
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expireAt))
                    if canExpire
                    else None
                ),
            },
        }
    except getUrlFailed as e:
        logger.error(
            f"获取{translateStrOrInt(source)}_{songId}_{translateStrOrInt(quality)}失败，原因：{e}"
        )
        return {
            "code": 500,
            "message": f"{e.args[0]}",
        }


async def getSongInfoForAPI(source, songId):
    try:
        cache = cacheM.get("info", f"{source}_{songId}")
        if cache:
            return {"code": 200, "message": "成功", "data": cache["data"]}
    except:
        pass

    try:
        func = require("modules.info." + source + ".getMusicInfo")
    except:
        return {
            "code": 404,
            "message": "未知的源或不支持的方法",
        }

    try:
        if source == "kg":
            result, _ = await func(songId)
        else:
            result: SongInfo = await func(songId)
        expireTime = 86400 * 3
        expireAt = int(time.time() + expireTime)
        if CACHE_ENABLE:
            cacheM.set(
                "info",
                f"{source}_{songId}",
                {
                    "data": result.__dict__,
                    "time": expireAt,
                    "expire": True,
                },
                expireTime,
            )
            logger.debug(f"缓存已更新：{source}_{songId}")
        return {"code": 200, "message": "成功", "data": result.__dict__}
    except getSongInfoFailed as e:
        return {
            "code": 500,
            "message": e.args[0],
        }


async def getLyricForAPI(source, songId):
    try:
        cache = cacheM.get("lyric", f"{source}_{songId}")
        if cache:
            return {"code": 200, "message": "成功", "data": cache["data"]}
    except:
        pass

    if source == "tx":
        try:
            songinfo = await info.tx.getMusicInfo(songId)
            songId = songinfo.songId
        except getSongInfoFailed as e:
            return {
                "code": 500,
                "message": e.args[0],
            }

    if source == "mg":
        try:
            song: Song = await url.mg.getUrl(songId, "128k")
            result = song.info.lyric
            expireTime = 86400 * 3
            expireAt = int(time.time() + expireTime)
            cacheM.set(
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
            return {"code": 200, "message": "成功", "data": result}
        except getLyricFailed as e:
            return {
                "code": 500,
                "message": e.args[0],
            }

    try:
        func = require("modules.lyric." + source + ".getLyric")
    except:
        return {
            "code": 404,
            "message": "未知的源或不支持的方法",
        }

    try:
        result = await func(songId)
        expireTime = 86400 * 3
        expireAt = int(time.time() + expireTime)
        if CACHE_ENABLE:
            cacheM.set(
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
        return {"code": 200, "message": "成功", "data": result}
    except getLyricFailed as e:
        return {
            "code": 500,
            "message": e.args[0],
        }
