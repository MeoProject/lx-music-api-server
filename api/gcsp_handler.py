import zlib
import time
from utils import orjson
import modules
import binascii

from fastapi import Request
from fastapi import Response
from fastapi import APIRouter

from server.config import config
from utils.log import createLogger
from utils.md5 import createMD5

from modules.lyric.kw import getLyric
from modules.info.kw import getMusicInfo
from utils.response import handleResponse

router = APIRouter()

logger = createLogger("GCSP Handler")


@router.get("/songinfoandlrc")
async def getKuwoOldInfo(request: Request, songId: int):
    Info = await getMusicInfo(songId)
    Lyrics = await getLyric(songId)
    SecondLyric = Lyrics["second_lyric"]
    return handleResponse(
        request,
        {
            "code": 200,
            "data": {
                "lrclist": SecondLyric,
                "songinfo": {
                    "pic": Info.coverUrl,
                },
            },
            "status": 200,
        },
    )


@router.api_route("/client/cgi-bin/{method}", methods=["GET", "POST"])
async def GcspApi(request: Request, method: str) -> Response:
    try:
        PACKAGE = config.read("modules.gcsp.package_md5")
        SALT_1 = config.read("modules.gcsp.salt_1")
        SALT_2 = config.read("modules.gcsp.salt_2")
        NEED_VERIFY = config.read("modules.gcsp.enable_verify")

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
            "sign": "[更新]",
        }

        def decode(indata: bytes) -> dict:
            return orjson.loads(binascii.unhexlify(zlib.decompress(indata)))

        def verify(data: dict) -> str:
            if not NEED_VERIFY:
                return "success"

            sign_1 = createMD5(PACKAGE + data["time"] + SALT_2)
            sign_2 = createMD5(
                str(
                    orjson.dumps(data["text_1"])
                    + orjson.dumps(data["text_2"])
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
                    orjson.dumps(
                        {
                            "code": "403",
                            "error_msg": internal_trans[result],
                            "data": None,
                        },
                    ).encode("utf-8")
                )
                return Response(
                    content=compressed_data,
                    media_type="application/octet-stream",
                )

            data["te"] = orjson.loads(data["text_1"])

            body = await modules.getUrlForAPI(
                pm[data["te"]["platform"]], data["te"]["t1"], qm[data["te"]["t2"]]
            )

            if body["code"] != 200:
                data = orjson.dumps({"code": "403", "error_msg": body["message"]})
            else:
                data = orjson.dumps(
                    {
                        "code": "200",
                        "error_msg": "success",
                        "data": body["url"] if body["code"] == 200 else None,
                    },
                )

            compressed_data = zlib.compress(data.encode("utf-8"))

            return Response(
                content=compressed_data, media_type="application/octet-stream"
            )

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
                        "version": config.read("modules.gcsp.update.ver"),
                        "update_title": config.read("modules.gcsp.update.title"),
                        "update_log": config.read("modules.gcsp.update.logs"),
                        "down_url": config.read("modules.gcsp.update.down_url"),
                        "share_url": config.read("modules.gcsp.update.pan_url"),
                        "compulsory": (
                            "yes"
                            if config.read("modules.gcsp.update.required")
                            else "no"
                        ),
                        "file_md5": PACKAGE,
                    },
                }
                req = await request.json()
                if req["clientversion"] != body["data"]["version"]:
                    return handleResponse(request, body)
                else:
                    return handleResponse(request, {"code": 404})
        else:
            return Response(content="Method Not Allowed", status_code=405)
    except:
        return handleResponse(request, {"code": 403, "error_message": "总之请求不成功"})
