import zlib
import time
import ujson
import modules
import binascii
from fastapi import Request
from fastapi import Response
from fastapi import APIRouter
from server.config import config
from utils.log import createLogger
from utils.md5 import createMD5
from utils.response import handleResponse

router = APIRouter()

logger = createLogger("GCSP Handler")


@router.api_route("/client/cgi-bin/{method}", methods=["GET", "POST"])
async def GcspApi(request: Request, method: str) -> Response:
    PACKAGE = config.read("module.gcsp.package_md5")
    SALT_1 = config.read("module.gcsp.salt_1")
    SALT_2 = config.read("module.gcsp.salt_2")
    NEED_VERIFY = config.read("module.gcsp.enable_verify")

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
        "sign": "需要更新",
    }

    def decode(indata: bytes) -> dict:
        return ujson.loads(binascii.unhexlify(zlib.decompress(indata)))

    def verify(data: dict) -> str:
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

    async def handleGcspBody(body: bytes):
        data = decode(body)

        result = verify(data)

        if result != "success":
            compressed_data = zlib.compress(
                ujson.dumps(
                    {"code": "403", "error_msg": internal_trans[result], "data": None},
                    ensure_ascii=False,
                ).encode("utf-8")
            )
            return Response(
                content=compressed_data,
                media_type="application/octet-stream",
            )

        data["te"] = ujson.loads(data["text_1"])

        body = await modules._url(
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

        return Response(content=compressed_data, media_type="application/octet-stream")

    if request.method == "POST":
        if method == "api.fcg":
            content_size = request.__len__()
            if content_size and content_size > 5 * 1024:
                return Response(content="Request Entity Too Large", status_code=413)
            body = await request.body()
            return await handleGcspBody(body)
        elif method == "check_version":
            body = {
                "code": "200",
                "data": {
                    "version": "2.1.0",
                    "update_title": "2.1.0",
                    "update_log": "",
                    "down_url": "",
                    "share_url": "",
                    "compulsory": "no",
                    "file_md5": PACKAGE,
                },
            }
            req = await request.json()
            if req["clientversion"] != body["data"]["version"]:
                return handleResponse(request, body)
            else:
                return handleResponse(request, {"code": 404})
        elif method == "zz":
            body1 = {
                "code": 200,
                "url": "",
                "text": "感谢支持",
            }  # 微信
            body2 = {
                "code": 200,
                "url": "",
                "text": "感谢支持",
            }  # 支付宝
            req = await request.json()
            if req["type"] == "wx":
                return handleResponse(request, body1)
            elif req["type"] == "zfb":
                return handleResponse(request, body2)
    elif request.method == "GET":
        if method == "Splash":
            return handleResponse(
                request,
                {
                    "state": "0",
                    "color": "white",
                    "status_bar_color": "white",
                    "imageUrl": "",
                },
            )
    else:
        return Response(content="Method Not Allowed", status_code=405)
