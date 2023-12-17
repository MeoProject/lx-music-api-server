# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: utils.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common import utils
from common import config
from common import Httpx

createObject = utils.CreateObject


tools = createObject({
    "signkey": config.read_config("module.kg.client.signatureKey"),
    "pidversec": config.read_config("module.kg.client.pidversionsecret"),
    "clientver": config.read_config("module.kg.client.clientver"),
    "x-router": config.read_config("module.kg.tracker.x-router"),
    "url": config.read_config("module.kg.tracker.host") + config.read_config("module.kg.tracker.path"),
    "version": config.read_config("module.kg.tracker.version"),
    "userid": config.read_config("module.kg.user.userid"),
    "token": config.read_config("module.kg.user.token"),
    "mid": config.read_config("module.kg.user.mid"),
    "extra_params": config.read_config("module.kg.tracker.extra_params"),
    "appid": config.read_config("module.kg.client.appid"),
    'qualityHashMap': {
        '128k': 'hash_128',
        '320k': 'hash_320',
        'flac': 'hash_flac',
        'flac24bit': 'hash_high',
        'master': 'hash_128',
    },
    'qualityMap': {
        '128k': '128',
        '320k': '320',
        'flac': 'flac',
        'flac24bit': 'high',
        'master': 'viper_atmos',
    },
})

def buildSignatureParams(dictionary, body = ""):
    joined_str = ''.join([f'{k}={v}' for k, v in dictionary.items()])
    return joined_str + body

def buildRequestParams(dictionary):
    joined_str = '&'.join([f'{k}={v}' for k, v in dictionary.items()])
    return joined_str

def sign(params, body = "", signkey = tools["signkey"]):
    params = utils.sortDict(params)
    params = buildSignatureParams(params, body)
    return utils.createMD5(signkey + params + signkey)

async def signRequest(url, params, options, signkey = tools["signkey"]):
    params['signature'] = sign(params, options.get("body") if options.get("body") else (options.get("data") if options.get("data") else ""), signkey)
    url = url + "?" + buildRequestParams(params)
    return await Httpx.AsyncRequest(url, options)

def getKey(hash_):
    return utils.createMD5(hash_.lower() + tools.pidversec + tools.appid + tools.mid + tools.userid)
