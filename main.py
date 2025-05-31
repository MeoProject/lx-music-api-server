import os
import shutil
import sys
import zlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import re
import time
import asyncio
import ujson
import modules
import binascii
import traceback
import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi.responses import (
    JSONResponse,
    StreamingResponse,
    FileResponse,
    HTMLResponse,
)
from common import (
    code,
    utils,
    config,
    scheduler,
    variable,
)
from common.log import log
from common.utils import IsLocalIP, createMD5
from common.request import GetIPInfo
from common.config import ReadConfig, CheckIPBanned, GetKeyInfo
from typing import List

with open("./statistics.json", "r") as f:
    content = f.read()
    status = ujson.loads(content)

app = FastAPI(
    version=variable.PackageInfo["version"],
    license_info={
        "name": "MIT",
        "identifier": "MIT",
    },
)
utils.setGlobal(app, "app")

logger = log("Main+FastAPI")
stopEvent = asyncio.exceptions.CancelledError


@app.middleware("http")
async def before(request: Request, call_next) -> dict | Response | JSONResponse | None:
    variable.StatsManager.increment("all_request")

    try:
        if ReadConfig("common.reverse_proxy.allow_proxy") and request.headers.get(
            ReadConfig("common.reverse_proxy.real_ip_header")
        ):
            if not (
                ReadConfig("common.reverse_proxy.allow_public_ip")
                or IsLocalIP(request.remote)
            ):
                return JSONResponse(
                    {"code": code.NOT_ACCEPT, "message": "不允许的公网IP转发"},
                    code.NOT_ACCEPT,
                )

            remote_addr = str(
                request.headers[ReadConfig("common.reverse_proxy.real_ip_header")]
            )
        else:
            remote_addr = request.client.host

        if CheckIPBanned(remote_addr):
            return JSONResponse(
                {"code": code.NOT_ACCEPT, "message": "IP is banned."}, code.NOT_ACCEPT
            )

        IPInfo = await GetIPInfo(remote_addr)

        logger.info(
            f"Req: {request.method} - {remote_addr} - {IPInfo['local']} - {request.url.path} - {request.headers['User-Agent']} - {request.url.query} - {request.headers.get('X-Request-Key', '')}"
        )

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        if isinstance(
            response,
            (Response, JSONResponse, StreamingResponse, FileResponse, HTMLResponse),
        ):
            response = response

        response.headers["X-Process-Time"] = str(process_time)

        return response
    except BaseException:
        logger.error(traceback.format_exc())
        return JSONResponse(
            {"code": code.SERVER_ERROR, "message": "服务器内部错误"}, code.SERVER_ERROR
        )
    except KeyboardInterrupt:
        return


@app.get("/", tags=["/"])
async def Home(request: Request):
    return {
        "code": code.SUCCESS,
        "message": "HELLO WORLD",
    }


@app.get("/url", tags=["url"])
@app.get("/lyric", tags=["lyric"])
@app.get("/info", tags=["info"])
async def Handle(
    request: Request,
    source: str,
    songId: str | int,
    quality: str | None = None,
) -> JSONResponse:
    enable, inlist = GetKeyInfo(request.headers.get("X-Request-Key", ""))

    method = request.url.path.split("/")[1]

    if not method:
        return JSONResponse(
            {"code": code.INVALID_REQUEST, "message": "参数缺失"}, code.INVALID_REQUEST
        )

    if method == "url" and quality is None:
        return JSONResponse(
            {"code": code.INVALID_REQUEST, "message": "必须参数: quality"},
            code.INVALID_REQUEST,
        )

    try:
        if source == "kg":
            songId = songId.lower()
        result = await getattr(modules, method)(source, songId, quality)
        return JSONResponse(result)
    except BaseException:
        logger.error(traceback.format_exc())
        return JSONResponse(
            {"code": code.SERVER_ERROR, "message": "内部服务器错误"}, code.SERVER_ERROR
        )


@app.get("/search", tags=["search"])
async def HandleSearch(
    source: str,
    keyword: str,
    pages: int,
    limit: int,
):
    try:
        result = await modules.search(source, keyword, pages, limit)
        return JSONResponse(result)
    except BaseException:
        logger.error(traceback.format_exc())
        return JSONResponse(
            {"code": code.SERVER_ERROR, "message": "内部服务器错误"}, code.SERVER_ERROR
        )


@app.get("/script", tags=["script"])
async def Script(
    request: Request,
    key: str | None = None,
):
    enable, inlist = GetKeyInfo(key)

    if (not inlist) and (enable):
        return JSONResponse(
            {"code": code.NOT_ACCEPT, "message": "Key错误"}, code.NOT_ACCEPT
        )

    try:
        with open(
            f"./data/script/lx-music-source-example.js", "r", encoding="utf-8"
        ) as f:
            script = f.read()
    except:
        return JSONResponse(
            {"code": code.NOT_FOUND, "message": "本地无源脚本"}, code.NOT_FOUND
        )

    scriptLines = script.split("\n")
    newScriptLines = []

    for line in scriptLines:
        oline = line
        line = line.strip()
        host = request.headers.get(
            ReadConfig("common.reverse_proxy.real_host_header"), ""
        )
        url = (
            f"{request.url.scheme}"
            + f"://{host if host else request.url.hostname}"
            + f":{request.url.port}"
            if request.url.port
            else None
        )
        if line.startswith("const API_URL"):
            newScriptLines.append(f'''const API_URL = "{url}"''')
        elif line.startswith("const API_KEY"):
            newScriptLines.append(f"""const API_KEY = `{key if key else ''''''}`""")
        elif line.startswith("* @name"):
            newScriptLines.append(
                " * @name " + ReadConfig("common.download_config.name")
            )
        elif line.startswith("* @description"):
            newScriptLines.append(
                " * @description " + ReadConfig("common.download_config.intro")
            )
        elif line.startswith("* @author"):
            newScriptLines.append(
                " * @author " + ReadConfig("common.download_config.author")
            )
        elif line.startswith("* @version"):
            newScriptLines.append(
                " * @version " + ReadConfig("common.download_config.version")
            )
        elif line.startswith("const DEV_ENABLE "):
            newScriptLines.append(
                "const DEV_ENABLE = "
                + str(ReadConfig("common.download_config.dev")).lower()
            )
        elif line.startswith("const UPDATE_ENABLE "):
            newScriptLines.append(
                "const UPDATE_ENABLE = "
                + str(ReadConfig("common.download_config.update")).lower()
            )
        else:
            newScriptLines.append(oline)

    r = "\n".join(newScriptLines)

    r = re.sub(
        r"const MUSIC_QUALITY = {[^}]+}",
        f'const MUSIC_QUALITY = JSON.parse(\'{ujson.dumps(ReadConfig("common.download_config.quality"))}\')',
        r,
    )

    if ReadConfig("common.download_config.update"):
        md5 = createMD5(r)
        r = r.replace(r'const SCRIPT_MD5 = "";', f'const SCRIPT_MD5 = "{md5}";')
        if request.query_params.get("checkUpdate"):
            if request.query_params.get("checkUpdate") == md5:
                return JSONResponse({"code": code.SUCCESS, "message": "成功"})
            url = (
                f"{request.url.scheme}"
                + f"://{host if host else request.url.hostname}"
                + f":{request.url.port}"
                if request.url.port
                else None
            )
            updateUrl = f"{url}/script{('?key=' + key) if key else ''}"
            updateMsg = (
                str(ReadConfig("common.download_config.updateMsg"))
                .format(
                    updateUrl=updateUrl,
                    url=url,
                    key=key,
                    version=ReadConfig("common.download_config.version"),
                )
                .replace("\\n", "\n")
            )
            return {
                "code": code.SUCCESS,
                "message": "成功",
                "data": {"updateMsg": updateMsg, "updateUrl": updateUrl},
            }

    return Response(
        r,
        media_type="text/javascript",
        headers={
            "Content-Disposition": f"""attachment; filename={
                            ReadConfig("common.download_config.filename")
                            if ReadConfig("common.download_config.filename").endswith(".js")
                            else (ReadConfig("common.download_config.filename") + ".js")}"""
        },
    )


@app.api_route("/client/cgi-bin/{method}", methods=["GET", "POST"])
async def gcsp(request: Request, method: str):
    PACKAGE = ReadConfig("gcsp.package_md5")
    SALT_1 = ReadConfig("gcsp.salt_1")
    SALT_2 = ReadConfig("gcsp.salt_2")
    NEED_VERIFY = ReadConfig("gcsp.enable_verify")
    ENABLE_PLATFORM = ReadConfig("gcsp.enable_source")

    qm = {
        "mp3": "128k",
        "hq": "320k",
        "sq": "flac",
        "hr": "hires",
        "hires": "hires",
        "dsd": "master",
    }

    pm = {"qq": "tx", "wyy": "wy", "kugou": "kg", "kuwo": "kw", "mgu": "mg"}

    internal_trans = {
        "time": "[禁止下载]请求检验失败，请检查系统时间是否为标准时间",
        "sign": "[更新]951962664, 一串数字自己想想",
    }

    def decode(indata) -> dict:
        return ujson.loads(binascii.unhexlify(zlib.decompress(indata)))

    def verify(data):
        if not NEED_VERIFY:
            return "success"
        sign_1 = createMD5(PACKAGE + data["time"] + SALT_2)
        sign_2 = createMD5(
            str(
                ujson.dumps(data["text_1"])
                + ujson.dumps(data["text_2"])
                + sign_1
                + data["time"]
                + SALT_1
            )
            .replace("\\", "")
            .replace('}"', "}")
            .replace('"{', "{")
        )
        if data["sign_1"] != sign_1 or data["sign_2"] != sign_2:
            return "sign"
        if int(time.time()) - int(data["time"]) > 10:
            return "time"
        return "success"

    async def handleGcspBody(body):
        data = decode(body)
        result = verify(data)

        t2 = ujson.loads(data["text_2"])

        logger.info(
            f"收到歌词适配请求，设备名称：{t2['device']}，设备ID：{t2['deviceid']}"
        )

        if result != "success":
            compressed_data = zlib.compress(
                ujson.dumps(
                    {"code": "403", "error_msg": internal_trans[result], "data": None},
                    ensure_ascii=False,
                ).encode("utf-8")
            )
            return Response(
                compressed_data,
                media_type="application/octet-stream",
            )

        data["te"] = ujson.loads(data["text_1"])

        if pm[data["te"]["platform"]] not in ENABLE_PLATFORM:
            compressed_data = zlib.compress(
                ujson.dumps(
                    {
                        "code": "403",
                        "error_msg": "此平台已停止服务",
                        "bitrate": 1,
                        "data": None,
                    },
                    ensure_ascii=False,
                ).encode("utf-8")
            )
            return Response(
                compressed_data,
                media_type="application/octet-stream",
            )

        body = await modules.url(
            pm[data["te"]["platform"]], data["te"]["t1"], qm[data["te"]["t2"]]
        )

        if body["code"] != 200:
            data = ujson.dumps(
                {"code": "403", "error_msg": body["message"]}, ensure_ascii=False
            )
        else:
            data = ujson.dumps(
                {
                    "code": "200",
                    "error_msg": "success",
                    "data": body["url"] if body["code"] == 200 else None,
                },
                ensure_ascii=False,
            )

        compressed_data = zlib.compress(data.encode("utf-8"))

        logger.info(f"歌词适配请求响应：{ujson.loads(data)}")

        return Response(compressed_data, media_type="application/octet-stream")

    if request.method == "POST":
        if method == "api.fcg":
            content_size = request.__len__()
            if content_size > 5 * 1024:
                return Response(body="Request Entity Too Large", status=413)
            body = await request.body()
            return await handleGcspBody(body)
        elif method == "check_version":
            body = {
                "code": "200",
                "data": {
                    "version": "2.0.8",
                    "update_title": "2.0.8",
                    "update_log": "更新启动图。",
                    "down_url": "",
                    "share_url": "",
                    "compulsory": "yes",
                    "file_md5": PACKAGE,
                },
            }

            req = await request.json()

            if req["clientversion"] != body["data"]["version"]:
                body = body
            else:
                body = {"code": 404}

            return body
        elif method == "zz":
            body1 = {
                "url": "",
                "text": "感谢支持",
            }  # 微信
            body2 = {
                "url": "",
                "text": "感谢支持",
            }  # 支付宝
            req = await request.json()
            if req["type"] == "wx":
                return body1
            elif req["type"] == "zfb":
                return body2
    elif request.method == "GET":
        if method == "Splash":
            return {
                "state": "0",
                "color": "white",
                "status_bar_color": "white",
                "imageUrl": "https://mf.ikunshare.top/歌词适配启动图.png",
            }
    else:
        return Response(body="Method Not Allowed", status=405)


@app.get("/subscription_{key}.json", tags=["subscription"])
async def GenMFScripts(request: Request, key: str):
    host = request.headers.get(ReadConfig("common.reverse_proxy.real_host_header"), "")

    url = (f"{request.url.scheme}" + f"://{host if host else request.url.hostname}") + (
        f":{request.url.port}" if request.url.port else None
    )

    enable, inlist = GetKeyInfo(key)

    if (not inlist) and (enable):
        return JSONResponse({"code": 403, "message": "Key错误"}, 403)

    try:
        subscription_data = ujson.loads(
            open("./data/musicfree/plugins.json", "r").read()
        )

        base_url = url
        for plugin in subscription_data["plugins"]:
            script_name = plugin["url"].split("/")[-2]
            plugin["url"] = f"{base_url}/script/{script_name}?key={key}"

        return JSONResponse(content=subscription_data, status_code=200)

    except Exception as e:
        return JSONResponse(
            {"code": 500, "message": f"处理订阅内容时出错: {str(e)}"}, 500
        )


@app.get("/script/{script_name}", tags=["script"])
async def GetModifiedScript(request: Request, script_name: str, key: str):
    host = request.headers.get(ReadConfig("common.reverse_proxy.real_host_header"), "")

    url = (f"{request.url.scheme}" + f"://{host if host else request.url.hostname}") + (
        f":{request.url.port}" if request.url.port else None
    )
    enable, inlist = GetKeyInfo(key)

    if (not inlist) and (enable):
        return JSONResponse({"code": 403, "message": "Key错误"}, 403)

    try:
        script_content = open(f"./data/musicfree/{script_name}/index.js", "r").read()

        modified_content = re.sub(
            r'const API_KEY = ".*?";', f'const API_KEY = "{key}";', script_content
        )

        if 'const API_URL = "";' in modified_content:
            modified_content = modified_content.replace(
                'const API_URL = "";', f'const API_URL = "{url}";'
            )

        if 'const API_KEY = "";' in modified_content:
            modified_content = modified_content.replace(
                'const API_KEY = "";', f'const API_KEY = "{key}";'
            )

        if 'const UPDATE_URL = "";' in modified_content:
            modified_content = modified_content.replace(
                'const UPDATE_URL = "";',
                f'const UPDATE_URL = "{url}/script/{script_name}?key={key}";',
            )

        return Response(
            content=modified_content,
            media_type="application/javascript",
            headers={
                "Content-Disposition": f"attachment; filename={script_name}_plugin.js"
            },
        )

    except Exception as e:
        return JSONResponse(
            {"code": 500, "message": f"处理脚本内容时出错: {str(e)}"}, 500
        )


from io import TextIOWrapper

for f in variable.LogFiles:
    if f and isinstance(f, TextIOWrapper):
        f.close()


async def clean():
    if variable.SyncClient:
        variable.SyncClient.close()
    if variable.AsyncClient:
        await variable.AsyncClient.close()
    if variable.StatsManager:
        variable.StatsManager.stop()

    logger.info("等待部分进程暂停...")


async def Init():
    if not os.path.exists("./data/script/lx-music-source-example.js"):
        shutil.copyfile(
            "./common/lx-music-source-example.js",
            "./data/script/lx-music-source-example.js",
        )
        logger.info("(1/4)已复制脚本")

    await scheduler.run()
    logger.info("(2/4)已执行定时任务")

    variable.StatsManager.start()
    logger.info("(3/4)已启动计数器")

    servers_config: List[uvicorn.Config] = []

    for bind in config.ReadConfig("common.binds"):
        ssl_params = {}
        if bind["scheme"] == "https":
            ssl_params = {
                "ssl_certfile": bind["ssl_cert_path"],
                "ssl_keyfile": bind["ssl_key_path"],
            }

            if not ssl_params["ssl_certfile"] or not ssl_params["ssl_keyfile"]:
                raise ValueError(f"HTTPS 配置 {bind['port']} 需要提供 SSL 证书路径")

        servers_config.append(
            uvicorn.Config(
                app,
                host=["0.0.0.0", "::"],
                port=int(bind["port"]),
                log_level="critical",
                access_log=None,
                **ssl_params,
            )
        )

    async def run_server(config: uvicorn.Config):
        try:
            logger.info("(4/4)已启动服务器")
            server = uvicorn.Server(config)
            await server.serve()
        except Exception as e:
            logger.error(f"Port {config.port} 启动失败: {e}")

    try:
        tasks = [run_server(config) for config in servers_config]
        await asyncio.gather(*tasks)
        await asyncio.Event().wait()
    except (stopEvent, KeyboardInterrupt):
        await clean()
        variable.Running = False
    except OSError as e:
        logger.error("遇到未知错误，请查看日志")
        logger.error(e)
    except:
        logger.error("遇到未知错误，请查看日志")
        logger.error(traceback.format_exc())
    finally:
        await clean()
        if variable.Running:
            variable.Running = False
        logger.info("服务器暂停")
        os._exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(Init())
    except:
        pass
