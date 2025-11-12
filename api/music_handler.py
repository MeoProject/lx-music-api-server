import modules
from fastapi import Request
from fastapi.routing import APIRouter
from utils.response import handleResponse

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
