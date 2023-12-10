#!/usr/bin/env python3

# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: main.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from aiohttp import web
from common import config
from common import lxsecurity
from common import utils
from common import log
from common import Httpx
from modules import handleApiRequest
import traceback
import time

logger = log.log("main")
aiologger = log.log('aiohttp_web')

Httpx.checkcn()

# check request info before start
async def handle_before_request(app, handler):
    async def handle_request(request):
        # nginx proxy header
        if (request.headers.get("X-Real-IP")):
            request.remote = request.headers.get("X-Real-IP")
        # check ip
        if (config.check_ip_banned(request.remote)):
            return utils.handleResult({"code": 1, "msg": "您的IP已被封禁", "data": None}, 403)
        # check global rate limit
        if (
            (time.time() - config.getRequestTime('global'))
            <
            (config.read_config("security.rate_limit.global"))
            ):
            return utils.handleResult({"code": 5, "msg": "全局限速", "data": None}, 429)
        if (
            (time.time() - config.getRequestTime(request.remote))
            <
            (config.read_config("security.rate_limit.ip"))
            ):
            return utils.handleResult({"code": 5, "msg": "IP限速", "data": None}, 429)
        # update request time
        config.updateRequestTime('global')
        config.updateRequestTime(request.remote)
        # check host
        if (config.read_config("security.allowed_host.enable")):
            if request.remote_host.split(":")[0] not in config.read_config("security.allowed_host.list"):
                if config.read_config("security.allowed_host.blacklist.enable"):
                    config.ban_ip(request.remote, int(config.read_config("security.allowed_host.blacklist.length")))
                return utils.handleResult({'code': 6, 'msg': '未找到您所请求的资源', 'data': None}, 404)
        try:
            resp = await handler(request)
            aiologger.info(f'{request.remote} - {request.method} "{request.path}", {resp.status}')
            return resp
        except web.HTTPException as ex:
            if ex.status == 500:  # 捕获500错误
                return utils.handleResult({"code": 4, "msg": "内部服务器错误", "data": None}, 500)
            else:
                logger.error(traceback.format_exc())
                return utils.handleResult({'code': 6, 'msg': '未找到您所请求的资源', 'data': None}, 404)
    return handle_request

async def main(request):
    return utils.handleResult({"code": 0, "msg": "success", "data": None})


async def handle(request):
    method = request.match_info.get('method')
    source = request.match_info.get('source')
    songId = request.match_info.get('songId')
    quality = request.match_info.get('quality')
    if (config.read_config("security.key.enable") and request.host.split(':')[0] not in config.read_config('security.whitelist_host')):
        if (request.headers.get("X-Request-Key")) != config.read_config("security.key.value"):
            if (config.read_config("security.key.ban")):
                config.ban_ip(request.remote)
            return utils.handleResult({"code": 1, "msg": "key验证失败", "data": None}, 403)
    if (config.read_config('security.check_lxm.enable') and request.host.split(':')[0] not in config.read_config('security.whitelist_host')):
        lxm = request.headers.get('lxm')
        if (not lxsecurity.checklxmheader(lxm, request.url)):
            if (config.read_config('security.lxm_ban.enable')):
                config.ban_ip(request.remote)
        return utils.handleResult({"code": 1, "msg": "lxm请求头验证失败", "data": None}, 403)
    
    try:
        return utils.handleResult(await handleApiRequest(method, source, songId, quality))
    except Exception as e:
        logger.error(traceback.format_exc())
        return utils.handleResult({'code': 4, 'msg': '内部服务器错误', 'data': None}, 500)

async def handle_404(request):
    return utils.handleResult({'code': 6, 'msg': '未找到您所请求的资源', 'data': None}, 404)

app = web.Application(middlewares=[handle_before_request])
# mainpage
app.router.add_get('/', main)

# api
app.router.add_get('/{method}/{source}/{songId}/{quality}', handle)

# 404
app.router.add_route('*', '/{tail:.*}', handle_404)

if (__name__ == "__main__"):
    try:
        web.run_app(app, host=config.read_config('common.host'), port=int(config.read_config('common.port')))
    except Exception as e:
        logger.error("服务器启动失败, 请查看下方日志")
        logger.error(traceback.format_exc())
        
