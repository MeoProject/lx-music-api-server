#!/usr/bin/env python3

# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: main.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

import sys

if ((sys.version_info.major == 3 and sys.version_info.minor < 6) or sys.version_info.major == 2):
    print('Python版本过低，请使用Python 3.6+ ')
    sys.exit(1)

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
import os

def handleResult(dic, status = 200) -> Response:
    return Response(body = json.dumps(dic, indent=2, ensure_ascii=False), content_type='application/json', status = status)

logger = log.log("main")
aiologger = log.log('aiohttp_web')

stopEvent = None
if (sys.version_info.minor < 8 and sys.version_info.major == 3):
    logger.warning('您使用的Python版本已经停止更新，不建议继续使用')
    import concurrent
    stopEvent = concurrent.futures._base.CancelledError
else:
    stopEvent = asyncio.exceptions.CancelledError

def start_checkcn_thread() -> None:
    threading.Thread(target=Httpx.checkcn).start()

# check request info before start
async def handle_before_request(app, handler):
    async def handle_request(request):
        try:
            if (config.read_config('common.reverse_proxy.allow_proxy')):
                if (request.headers.get(config.read_config('common.reverse_proxy.real_ip_header'))):
                    # proxy header
                    if (request.remote in config.read_config('common.reverse_proxy.proxy_whitelist_remote')):
                        request.remote_addr = request.headers.get(config.read_config('common.reverse_proxy.real_ip_header'))
                    else:
                        return handleResult({"code": 1, "msg": "反代客户端远程地址不在反代ip白名单中", "data": None}, 403)
                else:
                    request.remote_addr = request.remote
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
            aiologger.info(f'{request.remote_addr + ("" if (request.remote == request.remote_addr) else f"|proxy@{request.remote}")} - {request.method} "{request.path}", {resp.status}')
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
        query = dict(request.query)
        if (method in dir(modules) and query == {}):
            return handleResult(await getattr(modules, method)(source, songId, quality))
        elif ((method + '_with_query') in dir(modules) and query != {}):
            return handleResult(await getattr(modules, method + '_with_query')(source, songId, quality, query))
        else:
            if (query == {}):
                return handleResult(await modules.other(method, source, songId, quality))
            else:
                return handleResult(await modules.other_with_query(method, source, songId, quality, query))
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
    while True:
        try:
            host = config.read_config('common.host')
            ports = [int(port) for port in config.read_config('common.ports')]
            ssl_ports = [int(port) for port in config.read_config('common.ssl_info.ssl_ports')]
            
            final_ssl_ports = []
            final_ports = []
            for p in ports:
                if (p not in ssl_ports):
                    final_ports.append(p)
                else:
                    final_ssl_ports.append(p)
            # 读取证书和私钥路径
            cert_path = config.read_config('common.ssl_info.path.cert')
            privkey_path = config.read_config('common.ssl_info.path.privkey')

            # 创建 HTTP AppRunner
            http_runner = aiohttp.web.AppRunner(app)
            await http_runner.setup()

            # 启动 HTTP 端口监听
            for port in final_ports:
                http_site = aiohttp.web.TCPSite(http_runner, host, port)
                await http_site.start()
                logger.info(f"监听 -> http://{host}:{port}")

            if (config.read_config("common.ssl_info.enable") and final_ssl_ports != []):
                if (os.path.exists(cert_path) and os.path.exists(privkey_path)):
                    import ssl
                    # 创建 SSL 上下文，加载配置文件中指定的证书和私钥
                    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                    ssl_context.load_cert_chain(cert_path, privkey_path)

                    # 创建 HTTPS AppRunner
                    https_runner = aiohttp.web.AppRunner(app)
                    await https_runner.setup()

                    # 启动 HTTPS 端口监听
                    for port in ssl_ports:
                        https_site = aiohttp.web.TCPSite(https_runner, host, port, ssl_context=ssl_context)
                        await https_site.start()
                        logger.info(f"监听 -> https://{host}:{port}")

            return
        except OSError as e:
            if str(e).startswith("[Errno 98]"):
                logger.error("端口已被占用，请检查\n" + str(e))
                logger.info('服务器将在10s后再次尝试启动...')
                await asyncio.sleep(10)
                logger.info('重新尝试启动...')
            else:
                raise


async def initMain():
    await scheduler.run()
    variable.aioSession = aiohttp.ClientSession(trust_env=True)
    try:
        await run_app()
        logger.info("服务器启动成功，请按下Ctrl + C停止")
        await asyncio.Event().wait()  # 等待停止事件
    except (KeyboardInterrupt, stopEvent):
        pass
    except OSError as e:
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
