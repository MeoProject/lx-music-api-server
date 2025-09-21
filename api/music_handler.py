import modules
from fastapi import Request
from fastapi.routing import APIRouter
from utils.response import handleResponse

router = APIRouter()


@router.get("/url")
async def HandleSong(request: Request, source: str, songId: str | int, quality: str):
    if source == "kg":
        songId = songId.lower()

    result = await modules._url(source, songId, quality)
    return handleResponse(request, result)


@router.get("/info")
async def HandleSongInfo(request: Request, source: str, songId: str | int):
    if source == "kg":
        songId = songId.lower()

    result = await modules._info(source, songId)
    return handleResponse(request, result)


@router.get("/lyric")
async def HandleLyric(request: Request, source: str, songId: str | int):
    if source == "kg":
        songId = songId.lower()

    result = await modules._lyric(source, songId)
    return handleResponse(request, result)
