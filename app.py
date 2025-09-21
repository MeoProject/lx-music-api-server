import os
import asyncio

from api import (
    home_handler,
    gcsp_handler,
    script_handler,
    music_handler,
)

from middleware.auth import AuthMiddleware
from middleware.request_logger import RequestLoggerMiddleware

from fastapi import FastAPI
from fastapi import Request
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

import uvicorn
from uvicorn.config import Config

from server import variable
from server.config import config
from utils import scheduler


async def clean():
    if variable.http_client:
        await variable.http_client.aclose()
    logger.info("等待部分进程暂停...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        f"已加载\n"
        f"酷狗音乐账号{len(config.read('module.kg.users') or [])}个\n"
        f"QQ音乐账号{len(config.read('module.tx.users') or [])}个\n"
        f"网易云音乐账号{len(config.read('module.wy.users') or [])}个\n"
        f"咪咕音乐账号{len(config.read('module.mg.users') or [])}个"
    )
    await scheduler.run()
    yield

    await clean()
    server.should_exit = True
    if variable.running:
        variable.running = False
        logger.info("服务器暂停")
        os._exit(1)


app = FastAPI(debug=True, title="LX Music Api Server", lifespan=lifespan)

uvc = Config(
    "app:app",
    host=config.read("server.host"),
    port=config.read("server.port"),
    log_level="debug" if variable.debug else "error",
    reload=variable.debug,
)
server = uvicorn.Server(config=uvc)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)
app.add_middleware(RequestLoggerMiddleware)

stopEvent = asyncio.exceptions.CancelledError


app.include_router(home_handler.router)
app.include_router(script_handler.router)
app.include_router(music_handler.router)
if config.read("gcsp.enable"):
    app.include_router(gcsp_handler.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常")
    return {"code": 500, "message": f"未处理的异常: {exc}"}


from io import TextIOWrapper

for f in variable.log_files:
    if f and isinstance(f, TextIOWrapper):
        f.close()


async def init():
    try:
        await server.serve()
    except (stopEvent, KeyboardInterrupt):
        await clean()
        variable.running = False
    except Exception:
        logger.error("遇到错误，请查看日志")


if __name__ == "__main__":
    asyncio.run(init())
