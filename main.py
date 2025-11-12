from fastapi import FastAPI
from fastapi import Request
import asyncio
from pathlib import Path
from api import home_handler, gcsp_handler, script_handler, music_handler
from middleware.auth import AuthMiddleware
from middleware.request_logger import RequestLoggerMiddleware
from contextlib import asynccontextmanager
import uvicorn
from uvicorn.config import Config
from server import variable
from server.config import config
from utils import scheduler, log

logger = log.createLogger("FastAPI")


async def clean():
    if variable.http_client:
        await variable.http_client.connector.close()
        await variable.http_client.close()
    logger.info("等待部分进程暂停...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.intercept_print()
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
    "main:app",
    host=config.read("server.host"),
    port=config.read("server.port"),
    reload=config.read("server.reload"),
    workers=config.read("server.workers"),
)
server = uvicorn.Server(config=uvicorn_config)

app.add_middleware(AuthMiddleware)
app.add_middleware(RequestLoggerMiddleware)

stopEvent = asyncio.exceptions.CancelledError


app.include_router(home_handler.router)
app.include_router(script_handler.router)
app.include_router(music_handler.router)
if config.read("modules.gcsp.enable"):
    app.include_router(gcsp_handler.router)


@app.exception_handler(Exception)
async def globalErrorHandler(request: Request, exc: Exception):
    logger.error("未处理的异常")
    return {"code": 500, "message": f"未处理的异常: {exc}"}


from io import TextIOWrapper

for f in variable.log_files:
    if f and isinstance(f, TextIOWrapper):
        f.close()


if __name__ == "__main__":
    try:
        asyncio.run(server.serve())
    except:
        pass
