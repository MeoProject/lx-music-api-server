import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from server.config import config
from utils.log import createLogger
from utils.ip import getIPInfo

logger = createLogger("RequestLogger")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        if config.read("server.reverse_proxy"):
            request.state.remote_addr = str(
                request.headers[config.read("server.real_ip")]
            )
            request.state.host = request.base_url.hostname
            request.state.proto = str(request.headers[config.read("server.proto")])
        else:
            request.state.remote_addr = request.client.host
            request.state.host = request.base_url.hostname
            request.state.proto = request.base_url.scheme

        try:
            ip_info = await getIPInfo(request.state.remote_addr)
        except:
            ip_info = {"local": "Unknown"}

        logger.info(
            f"请求: {request.method} - {request.state.remote_addr} - "
            f"{ip_info['local']} - {request.url.path} - "
            f"{request.headers.get('User-Agent', '')} - "
        )

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        return response
