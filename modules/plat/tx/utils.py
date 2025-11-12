import time
from modules.plat.tx.sign import signBody
from utils import orjson
from utils.http import HttpRequest
from server.config import config


async def getSign(data: dict) -> str:
    body = orjson.dumps(data)
    params = "&".join(
        [
            str(data["comm"]["ct"]),
            str(data["comm"]["v"]),
            "null",
            "null",
            str(int(time.time()) * 1000),
            str(data["comm"]["udid"]),
            "android",
        ]
    )

    req = await HttpRequest(
        f"{config.read('modules.platform.tx.sign_server_url')}/sign",
        {
            "method": "POST",
            "body": orjson.dumps(
                {
                    "body": body,
                    "params": params,
                }
            ),
        },
    )

    resp = req.json()
    sign = resp.get("sign", "")
    mask = resp.get("mask", "")

    return sign, mask, body


async def signRequest(data):
    if config.read("modules.platform.tx.sign_server_url") not in [None, ""]:
        sign, mask, body = await getSign(data)

        return await HttpRequest(
            "https://u.y.qq.com/cgi-bin/musics.fcg",
            {
                "method": "POST",
                "body": body,
                "headers": {
                    "sign": sign,
                    "mask": mask,
                    "x-sign-data-type": "json",
                },
            },
        )
    else:
        body = orjson.dumps(data)
        return await HttpRequest(
            "https://u.y.qq.com/cgi-bin/musics.fcg" + signBody(body),
            {
                "method": "POST",
                "body": body,
            },
        )
