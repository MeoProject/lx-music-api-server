import ujson
import random
from common import utils
from common import config
from common import request

tools = {
    "mid": random.choice(config.ReadConfig("module.kg.mid")),
    "offcial": {
        "appid": "1005",
        "signkey": "OIlwieks28dk2k092lksi2UIkp",
        "pidversec": "57ae12eb6890223e355ccfcb74edf70d",
        "clientver": "12029",
        "pid": "2",
    },
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


def sign(params, body="", signkey=None):
    if isinstance(body, dict):
        body = ujson.dumps(body)
    params = utils.sortDict(params)
    params = buildSignatureParams(params, body)
    return utils.createMD5(signkey + params + signkey)


async def signRequest(url, params, options, signkey=None, version="offcial"):
    if not signkey:
        signkey = tools[version]["signkey"]

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
        signkey,
    )
    url = url + "?" + buildRequestParams(params)
    return await request.AsyncRequest(url, options)


def getKey(hash_, user_info):
    return utils.createMD5(
        hash_.lower()
        + tools[user_info["version"]]["pidversec"]
        + tools[user_info["version"]]["appid"]
        + tools["mid"]
        + user_info["userid"]
    )
