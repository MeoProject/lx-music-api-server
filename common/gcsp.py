# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: gcsp.py - 
# - project: moonsea_api(private) - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "moonsea_api" project and featured for the "lx-music-api-server" project.

import zlib
import binascii
import time
import ujson as json
import modules
from .utils import createMD5 as hashMd5
from . import config
from aiohttp.web import Response

PACKAGE = config.read_config("module.gcsp.package_md5") # pkg md5
SALT_1 = config.read_config("module.gcsp.salt_1") # salt 1
SALT_2 = config.read_config("module.gcsp.salt_2") # salt 2
NEED_VERIFY = config.read_config("module.gcsp.enable_verify") # need verify

qm = {
    'mp3': '128k',
    'hq': '320k',
    'sq': 'flac',
    "hr": "flac24bit",
    'hires': 'flac24bit'
}

pm = {
    'qq': 'tx',
    'wyy': 'wy',
    'kugou': 'kg',
    "kuwo": "kw",
    "mgu": "mg"
}

internal_trans = {
    "time": "请求检验失败，请检查系统时间是否为标准时间",
    "sign": "请求检验失败，请检查应用是否被修改或更新到最新版本",
}

def decode(indata):
    return json.loads(binascii.unhexlify(zlib.decompress(indata)))

def verify(data):
    if (not NEED_VERIFY):
        return "success"
    sign_1 = hashMd5(PACKAGE + data["time"] + SALT_2)
    sign_2 = hashMd5((json.dumps(data["text_1"]) + json.dumps(data["text_2"]) + sign_1 + data["time"] + SALT_1).replace("\\", "").replace("}\"", "}").replace("\"{", "{"))

    if (data["sign_1"] != sign_1 or data["sign_2"] != sign_2):
        return "sign"
    if int(time.time()) - int(data["time"]) > 10:
        return "time"
    return "success"

async def handleGcspBody(body):
    data = decode(body)
    result = verify(data)
    if (result != "success"):
        return zlib.compress(json.dumps({"code": "403", "error_msg": internal_trans[result], "data": None}, ensure_ascii = False).encode("utf-8")), 200

    data["te"] = json.loads(data["text_1"])

    body = modules.url(pm[data["te"]["platform"]], data["te"]["t1"], qm[data["te"]["t2"]])

    if (body["code"] == 0):
        return zlib.compress(json.dumps({"code": "200", "error_msg": "success", "data": body["data"] if (pm[data["te"]["platform"]] != "kw") else {"bitrate": "123", "url": body["data"]}}, ensure_ascii = False).encode("utf-8")), 200
    else:
        return zlib.compress(json.dumps({"code": "403", "error_msg": "内部系统错误，请稍后再试", "data": None}, ensure_ascii = False).encode("utf-8")), 200

async def handle_request(request):
    if (request.method == "POST"):
        body = await request.body()
        return Response(
            body = await handleGcspBody(body),
            content_type = "application/octet-stream"
        )
    else:
        return Response(
            body = "Method Not Allowed",
            status = 405
        )