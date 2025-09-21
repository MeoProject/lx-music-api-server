import time

from utils import log
from .constants import (
    Source_Quality_Map,
    sourceExpirationTime,
    sourceNameTranslate,
    QualityNameTranslate,
)
from server.config import config, cache as cacheM
from models import Song, SongInfo, UrlResponse
from server.exceptions import getUrlFailed

from . import plat
from . import refresh
from . import url
from . import lyric
from . import info
from . import search

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


async def _url(source: str, songId: str, quality: str) -> dict:
    if quality == "flac24bit":
        quality = "hires"

    if quality not in Source_Quality_Map[source]:
        return {
            "code": 400,
            "message": "参数quality不正确, 此平台支持音质在下面",
            "support_quality": Source_Quality_Map[source],
        }

    if CACHE_ENABLE:
        try:
            cache = cacheM.get("urls", f"{source}_{songId}_{quality}")
            if cache:
                cache = dict(cache)
                logger.info(
                    f"使用缓存的{sourceNameTranslate[source]}_{songId}_{QualityNameTranslate[quality]}数据, URL: {cache['url']}"
                )

                result = Song(
                    SongInfo(**cache["info"]),
                    UrlResponse(**cache["url"]),
                )

                return {
                    "code": 200,
                    "message": "成功",
                    "url": result.url.url,
                    "ekey": result.url.ekey,
                    "quality": QualityNameTranslate[result.url.quality],
                    "info": result.info.__dict__,
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
        except Exception:
            logger.error(
                f"获取缓存{sourceNameTranslate[source]}_{songId}_{QualityNameTranslate[quality]}失败"
            )

    try:
        func = require(f"modules.url.{source}.getUrl")
    except:
        return {
            "code": 404,
            "message": "未知的源或不支持的方法",
        }

    try:
        result: Song = await func(songId, quality)
        logger.info(
            "获取%s_%s_%s_%s_%s成功, URL: %s"
            % (
                sourceNameTranslate[source],
                songId,
                result.info.songName,
                result.info.artistName,
                QualityNameTranslate[quality],
                result.url.url,
            )
        )
        canExpire = sourceExpirationTime[source]["expire"]
        expireTime = int(sourceExpirationTime[source]["time"] * 0.75)
        expireAt = int(expireTime + time.time())
        if CACHE_ENABLE:
            cacheM.set(
                "urls",
                f"{source}_{songId}_{quality}",
                {
                    "time": expireAt,
                    "expire": canExpire,
                    "url": result.url.__dict__,
                    "info": result.info.__dict__,
                },
                expireTime if canExpire else None,
            )
            logger.info(
                "缓存已更新: %s_%s_%s, URL: %s, Expire: %s"
                % (
                    sourceNameTranslate[source],
                    songId,
                    QualityNameTranslate[quality],
                    result.url.url,
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expireAt)),
                )
            )

        return {
            "code": 200,
            "message": "成功",
            "url": result.url.url,
            "ekey": result.url.ekey,
            "quality": QualityNameTranslate[result.url.quality],
            "info": result.info.__dict__,
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
            f"获取{sourceNameTranslate[source]}_{songId}_{QualityNameTranslate[quality]}失败，原因：{e}"
        )
        return {
            "code": 500,
            "message": f"{e.args[0]}",
        }


async def _search(source: str, keyword: str, pages: int, limit: int) -> dict:
    try:
        func = require("modules.search.{source}.search")
    except:
        return {"code": 404, "message": "未知的源或不支持的方法"}

    try:
        result = await func(keyword, pages, limit)
        return {"code": 200, "message": "成功", "result": result}
    except Exception as e:
        return {"code": 500, "message": e.args[0]}
