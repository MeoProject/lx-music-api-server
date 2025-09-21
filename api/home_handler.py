from fastapi import APIRouter, Request
from utils.response import handleResponse

router = APIRouter()


@router.get("/")
async def home(request: Request):
    """主页欢迎接口"""
    return handleResponse(
        request=request,
        body={"code": 200, "message": "HELLO WORLD"},
    )
