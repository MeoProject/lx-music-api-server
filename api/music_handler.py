import modules
from fastapi import Request
from fastapi.routing import APIRouter
from modules.url.tx import getEncryptedUrl
from server.exceptions import getSongInfoFailed, getUrlFailed
from server.config import cache
from utils.response import handleResponse
from server.models import UrlResponse

router = APIRouter()


@router.get("/url")
async def handleSongUrl(request: Request, source: str, songId: str | int, quality: str):
    if source == "kg":
        songId = songId.lower()

    result = await modules.getUrlForAPI(source, songId, quality)
    return handleResponse(request, result)


@router.get("/info")
async def handleSongInfo(request: Request, source: str, songId: str | int):
    if source == "kg":
        songId = songId.lower()

    result = await modules.getSongInfoForAPI(source, songId)
    return handleResponse(request, result)


@router.get("/lyric")
async def handleLyric(request: Request, source: str, songId: str | int):
    if source == "kg":
        songId = songId.lower()

    result = await modules.getLyricForAPI(source, songId)
    return handleResponse(request, result)


@router.get("/eurl")
async def handleEncryptSongUrl(request: Request, songId: str | int, quality: str):
    try:
        cache_data = cache.get("eurl", f"{songId}_{quality}")
        result = UrlResponse(**cache_data)
        print(
            f"获取缓存的Encrypt_QM_{songId}_{quality}成功, URL: {result.url}, Ekey: {result.ekey:10}"
        )
        return handleResponse(
            request,
            {"code": 200, "message": "成功", "url": result.url, "ekey": result.ekey},
        )
    except:
        pass

    try:
        result = await getEncryptedUrl(songId, quality)
        print(
            f"获取Encrypt_QM_{songId}_{quality}成功, URL: {result.url}, Ekey: {result.ekey:10}"
        )
        cache.set("eurl", f"{songId}_{quality}", result.__dict__, 600)
        print(f"缓存已更新: Encrypt_QM_{songId}_{quality}")
        return handleResponse(
            request,
            {"code": 200, "message": "成功", "url": result.url, "ekey": result.ekey},
        )
    except getUrlFailed as e:
        return handleResponse(request, {"code": 500, "message": f"获取链接失败：{e}"})
    except getSongInfoFailed as e:
        return handleResponse(request, {"code": 500, "message": f"获取详情失败：{e}"})
