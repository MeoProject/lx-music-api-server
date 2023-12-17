#!/usr/bin/env python3

# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: main-flask.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you know what you are doing.

# flask
from flask import Flask, request

# create flask app
app = Flask("LXMusicTestAPI")

# redirect the default flask logging to custom
import logging
from common import config
from common import log

flask_logger = log.log('flask')
logging.getLogger('werkzeug').addHandler(log.LogHelper(flask_logger))
logger = log.log("main")

from common import lxsecurity
from common import Httpx
from flask import Response
import threading
import ujson as json
import traceback
import modules
import time
threading.Thread(target=Httpx.checkcn).start()

def handleResult(dic):
    return Response(json.dumps(dic, indent=2, ensure_ascii=False), mimetype='application/json')

@app.route('/')
def index():
    return handleResult({"code": 0, "msg": "success", "data": None}), 200

@app.route('/<method>/<source>/<songId>/<quality>')
async def handle(method, source, songId, quality):
    if (config.read_config("security.key.enable") and request.host.split(':')[0] not in config.read_config('security.whitelist_host')):
        if (request.headers.get("X-Request-Key")) != config.read_config("security.key.value"):
            if (config.read_config("security.key.ban")):
                config.ban_ip(request.remote_addr)
            return handleResult({"code": 1, "msg": "key验证失败", "data": None}), 403
    if (config.read_config('security.check_lxm.enable') and request.host.split(':')[0] not in config.read_config('security.whitelist_host')):
        lxm = request.headers.get('lxm')
        if (not lxsecurity.checklxmheader(lxm, request.url)):
            if (config.read_config('security.lxm_ban.enable')):
                config.ban_ip(request.remote_addr)
        return handleResult({"code": 1, "msg": "lxm请求头验证失败", "data": None}), 403
    
    if method == 'url':
        try:
            return handleResult(await getattr(modules, method)(source, songId, quality))
        except Exception as e:
            logger.error(traceback.format_exc())
            return handleResult({'code': 4, 'msg': '内部服务器错误', 'data': None}), 500
    else:
        return handleResult({'code': 6, 'msg': '未知的请求类型: ' + method, 'data': None}), 400

@app.errorhandler(500)
def _500(_):
    return handleResult({'code': 4, 'msg': '内部服务器错误', 'data': None}), 500

@app.errorhandler(404)
def _404(_):
    return handleResult({'code': 6, 'msg': '未找到您所请求的资源', 'data': None}), 404

@app.before_request
def check():
    # nginx proxy header
    if (request.headers.get("X-Real-IP")):
        request.remote_addr = request.headers.get("X-Real-IP")
    # check ip
    if (config.check_ip_banned(request.remote_addr)):
        return handleResult({"code": 1, "msg": "您的IP已被封禁", "data": None}), 403
    # check global rate limit
    if ((time.time() - config.getRequestTime('global')) <= (config.read_config("security.rate_limit.global"))):
        return handleResult({"code": 5, "msg": "全局限速", "data": None}), 429
    if ((time.time() - config.getRequestTime(request.remote_addr)) <= (config.read_config("security.rate_limit.ip"))):
        return handleResult({"code": 5, "msg": "IP限速", "data": None}), 429
    # update request time
    config.updateRequestTime('global')
    config.updateRequestTime(request.remote_addr)
    # check host
    if (config.read_config("security.allowed_host.enable")):
        if request.remote_host.split(":")[0] not in config.read_config("security.allowed_host.list"):
            if config.read_config("security.allowed_host.blacklist.enable"):
                config.ban_ip(request.remote_addr, int(config.read_config("security.allowed_host.blacklist.length")))
            return handleResult({'code': 6, 'msg': '未找到您所请求的资源', 'data': None}), 404

if (__name__ == '__main__'):
    # run
    app.run(host=config.read_config('common.host'), port=config.read_config('common.port'))
