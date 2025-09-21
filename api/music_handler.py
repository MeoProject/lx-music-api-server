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


@router.get("/search")
async def HandleSearch(
    request: Request, source: str, keyword: str, pages: int = 1, limit: int = 30
):
    try:
        result = await modules._search(source, keyword, pages, limit)
        return handleResponse(request, result)
    except Exception:
        return handleResponse(
            request,
            {"code": 500, "message": "内部服务器错误"},
        )
