#!/usr/bin/env python3

# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: main.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common import config
from common import lxsecurity
from common import log
from common import Httpx
from common import variable
from common import scheduler
from common import lx_script
from aiohttp.web import Response
import ujson as json
import threading
import traceback
import modules
import asyncio
import aiohttp
import time

def handleResult(dic, status = 200):
    return Response(body = json.dumps(dic, indent=2, ensure_ascii=False), content_type='application/json', status = status)

logger = log.log("main")
aiologger = log.log('aiohttp_web')

def start_checkcn_thread():
    threading.Thread(target=Httpx.checkcn).start()

# check request info before start
async def handle_before_request(app, handler):
    async def handle_request(request):
        try:
            # nginx proxy header
            if (request.headers.get("X-Real-IP")):
                request.remote_addr = request.headers.get("X-Real-IP")
            else:
                request.remote_addr = request.remote
            # check ip
            if (config.check_ip_banned(request.remote_addr)):
                return handleResult({"code": 1, "msg": "您的IP已被封禁", "data": None}, 403)
            # check global rate limit
            if (
                (time.time() - config.getRequestTime('global'))
                <
                (config.read_config("security.rate_limit.global"))
                ):
                return handleResult({"code": 5, "msg": "全局限速", "data": None}, 429)
            if (
                (time.time() - config.getRequestTime(request.remote_addr))
                <
                (config.read_config("security.rate_limit.ip"))
                ):
                return handleResult({"code": 5, "msg": "IP限速", "data": None}, 429)
            # update request time
            config.updateRequestTime('global')
            config.updateRequestTime(request.remote_addr)
            # check host
            if (config.read_config("security.allowed_host.enable")):
                if request.host.split(":")[0] not in config.read_config("security.allowed_host.list"):
                    if config.read_config("security.allowed_host.blacklist.enable"):
                        config.ban_ip(request.remote_addr, int(config.read_config("security.allowed_host.blacklist.length")))
                    return handleResult({'code': 6, 'msg': '未找到您所请求的资源', 'data': None}, 404)

            resp = await handler(request)
            if (isinstance(resp, str)):
                resp = Response(body = resp, content_type='text/plain', status = 200)
            elif (isinstance(resp, dict)):
                resp = handleResult(resp)
            elif (not isinstance(resp, Response)):
                resp = Response(body = str(resp), content_type='text/plain', status = 200)
            aiologger.info(f'{request.remote_addr} - {request.method} "{request.path}", {resp.status}')
            return resp
        except: 
            logger.error(traceback.format_exc())
            return {"code": 4, "msg": "内部服务器错误", "data": None}
    return handle_request

async def main(request):
    return handleResult({"code": 0, "msg": "success", "data": None})


async def handle(request):
    method = request.match_info.get('method')
    source = request.match_info.get('source')
    songId = request.match_info.get('songId')
    quality = request.match_info.get('quality')
    if (config.read_config("security.key.enable") and request.host.split(':')[0] not in config.read_config('security.whitelist_host')):
        if (request.headers.get("X-Request-Key")) != config.read_config("security.key.value"):
            if (config.read_config("security.key.ban")):
                config.ban_ip(request.remote_addr)
            return handleResult({"code": 1, "msg": "key验证失败", "data": None}, 403)
    if (config.read_config('security.check_lxm.enable') and request.host.split(':')[0] not in config.read_config('security.whitelist_host')):
        lxm = request.headers.get('lxm')
        if (not lxsecurity.checklxmheader(lxm, request.url)):
            if (config.read_config('security.lxm_ban.enable')):
                config.ban_ip(request.remote_addr)
        return handleResult({"code": 1, "msg": "lxm请求头验证失败", "data": None}, 403)
    
    try:
        if (method in dir(modules)):
            return handleResult(await getattr(modules, method)(source, songId, quality))
        else:
            return handleResult(await modules.other(method, source, songId, quality))
    except:
        logger.error(traceback.format_exc())
        return handleResult({'code': 4, 'msg': '内部服务器错误', 'data': None}, 500)

async def handle_404(request):
    return handleResult({'code': 6, 'msg': '未找到您所请求的资源', 'data': None}, 404)

app = aiohttp.web.Application(middlewares=[handle_before_request])
# mainpage
app.router.add_get('/', main)

# api
app.router.add_get('/{method}/{source}/{songId}/{quality}', handle)
app.router.add_get('/{method}/{source}/{songId}', handle)

if (config.read_config('common.allow_download_script')):
    app.router.add_get('/script', lx_script.generate_script_response)

# 404
app.router.add_route('*', '/{tail:.*}', handle_404)


async def run_app():
    host = config.read_config('common.host')
    port = int(config.read_config('common.port'))
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, host, port)
    await site.start()
    logger.info(f"监听 -> http://{host}:{port}")

async def initMain():
    await scheduler.run()
    variable.aioSession = aiohttp.ClientSession()
    try:
        await run_app()
        logger.info("服务器启动成功，请按下Ctrl + C停止")
        await asyncio.Event().wait()  # 等待停止事件
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        pass
    except OSError as e:
        if str(e).startswith("[Errno 98]"):
            logger.error("端口已被占用，请检查\n" + str(e))
        else:
            logger.error("遇到未知错误，请查看日志")
            logger.error(traceback.format_exc())
    except:
        logger.error("遇到未知错误，请查看日志")
        logger.error(traceback.format_exc())
    finally:
        logger.info('wating for sessions to complete...')
        if variable.aioSession:
            await variable.aioSession.close()
        
        variable.running = False
        logger.info("Server stopped")

if __name__ == "__main__":
    try:
        start_checkcn_thread()
        asyncio.run(initMain())
    except KeyboardInterrupt:
        pass
    except:
        logger.error('初始化出错，请检查日志')
        logger.error(traceback.format_exc())