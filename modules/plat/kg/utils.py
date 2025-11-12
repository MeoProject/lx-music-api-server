from utils import orjson
from utils import http as request
from utils.dict import sortDict
from utils.md5 import createMD5

tools = {
    "mid": "musicapi",
    "qualityHashMap": {
        "128k": "hash_128",
        "320k": "hash_320",
        "flac": "hash_flac",
        "hires": "hash_high",
        "atmos": "hash_128",
        "master": "hash_128",
    },
    "qualityMap": {
        "128k": "128",
        "320k": "320",
        "flac": "flac",
        "hires": "high",
        "atmos": "viper_atmos",
        "master": "viper_clear",
    },
}


def buildSignatureParams(dictionary, body=""):
    joined_str = "".join([f"{k}={v}" for k, v in dictionary.items()])
    return joined_str + body


def buildRequestParams(dictionary: dict):
    joined_str = "&".join([f"{k}={v}" for k, v in dictionary.items()])
    return joined_str


def sign(params, body=""):
    if isinstance(body, dict):
        body = orjson.dumps(body)

    params = sortDict(params)
    params = buildSignatureParams(params, body)

    return createMD5(
        "OIlwieks28dk2k092lksi2UIkp" + params + "OIlwieks28dk2k092lksi2UIkp"
    )


async def signRequest(url: str, params: dict, options: dict) -> request.Response:
    params["signature"] = sign(
        params,
        (
            options.get("body")
            if options.get("body")
            else (
                options.get("data")
                if options.get("data")
                else (options.get("json") if options.get("json") else "")
            )
        ),
    )
    url = url + "?" + buildRequestParams(params)
    return await request.HttpRequest(url, options)


def getKey(hash_: str, user_info: dict[str, str]) -> str:
    return createMD5(
        hash_.lower()
        + "57ae12eb6890223e355ccfcb74edf70d"
        + "1005"
        + tools["mid"]
        + user_info["userid"]
    )
