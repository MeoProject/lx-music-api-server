import asyncio

from api import home_handler, gcsp_handler, script_handler, music_handler, qmc_handler

from middleware.auth import AuthMiddleware
from middleware.request_logger import RequestLoggerMiddleware

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

import uvicorn
from uvicorn.config import Config

from server import variable
from server.config import config
from utils import scheduler, log

logger = log.createLogger("FastAPI")


async def clean():
    if variable.http_client:
        await variable.http_client.aclose()
    logger.info("等待部分进程暂停...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"服务器启动于http://{server.config.host}:{server.config.port}")
    print(
        f"已加载\n"
        f"酷狗音乐账号{len(config.read('module.platform.kg.users') or [])}个\n"
        f"QQ音乐账号{len(config.read('module.platform.tx.users') or [])}个\n"
        f"网易云音乐账号{len(config.read('module.platform.wy.users') or [])}个\n"
        f"咪咕音乐账号{len(config.read('module.platform.mg.users') or [])}个"
    )
    await scheduler.run()
    yield

    await clean()
    server.should_exit = True
    if variable.running:
        variable.running = False
        logger.info("服务器暂停")


app = FastAPI(
    debug=config.read("server.debug"), title="LX Music Api Server", lifespan=lifespan
)

uvicorn_config = Config(
    "app:app",
    host=config.read("server.host"),
    port=config.read("server.port"),
    reload=config.read("server.reload"),
    workers=config.read("server.workers"),
    log_config=None,
    log_level=None,
    access_log=False,
)
server = uvicorn.Server(config=uvicorn_config)

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
if config.read("module.gcsp.enable"):
    app.include_router(gcsp_handler.router)
if config.read("module.qmc_decrypter"):
    app.include_router(qmc_handler.router)


@app.exception_handler(Exception)
async def globalErrorHandler(request: Request, exc: Exception):
    logger.error(f"未处理的异常")
    return {"code": 500, "message": f"未处理的异常: {exc}"}


from io import TextIOWrapper

for f in variable.log_files:
    if f and isinstance(f, TextIOWrapper):
        f.close()


async def Init():
    try:
        await server.serve()
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    try:
        asyncio.run(Init())
    except:
        pass
