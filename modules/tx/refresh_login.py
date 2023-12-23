# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: refresh_login.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common import Httpx
from common import scheduler
from common import config
from common import log
from .utils import sign
import ujson as json

logger = log.log('qqmusic_refresh_login')

async def refresh():
    if (not config.read_config('module.tx.user.qqmusic_key')):
        return
    if (not config.read_config('module.tx.refresh_login.enable')):
        return
    if (config.read_config('module.tx.user.qqmusic_key').startswith('W_X')):
        options = {
            'method': 'POST',
            'body': json.dumps({
                "comm": {
                    "fPersonality": "0",
                    "tmeLoginType": "1",
                    "tmeLoginMethod": "1",
                    "qq": "",
                    "authst": "",
                    "ct": "11",
                    "cv": "12080008",
                    "v": "12080008",
                    "tmeAppID": "qqmusic"
                },
                "req1": {
                    "module": "music.login.LoginServer",
                    "method": "Login",
                    "param": {
                        "code": "",
                        "openid": "",
                        "refresh_token": "",
                        "str_musicid": str(config.read_config('module.tx.user.uin')),
                        "musickey": config.read_config('module.tx.user.qqmusic_key'),
                        "unionid": "",
                        "refresh_key": "",
                        "loginMode": 2
                    }
                }
            })
        }
        signature = sign(options['body'])
        req = await Httpx.AsyncRequest(f'https://u.y.qq.com/cgi-bin/musics.fcg?sign={signature}', options)
        body = req.json()
        if (body['req1']['code'] != 0):
            logger.warning('刷新登录失败, code: ' +
                           str(body['req1']['code']) + f'\n响应体: {body}')
            return
        else:
            logger.info('刷新登录成功')
            config.write_config('module.tx.user.uin',
                                body['req1']['data']['musicid'])
            logger.info('已通过相应数据更新uin')
            config.write_config('module.tx.user.qqmusic_key',
                                body['req1']['data']['musickey'])
            logger.info('已通过相应数据更新qqmusic_key')
    elif (config.read_config('module.tx.user.qqmusic_key').startswith('Q_H_L')):
        options = {
            'method': 'POST',
            'body': json.dumps({
                'req1': {
                    'module': 'QQConnectLogin.LoginServer',
                    'method': 'QQLogin',
                    'param': {
                        'expired_in': 7776000,
                        'musicid': int(config.read_config('module.tx.user.uin')),
                        'musickey': config.read_config('module.tx.user.qqmusic_key')
                    }
                }
            })
        }
        signature = sign(options['body'])
        req = await Httpx.AsyncRequest(f'https://u6.y.qq.com/cgi-bin/musics.fcg?sign={signature}', options)
        body = req.json()
        if (body['req1']['code'] != 0):
            logger.warning('刷新登录失败, code: ' +
                           str(body['req1']['code']) + f'\n响应体: {body}')
            return
        else:
            logger.info('刷新登录成功')
            config.write_config('module.tx.user.uin',
                                body['req1']['data']['musicid'])
            logger.info('已通过相应数据更新uin')
            config.write_config('module.tx.user.qqmusic_key',
                                body['req1']['data']['musickey'])
            logger.info('已通过相应数据更新qqmusic_key')
    else:
        logger.error('未知的qqmusic_key格式')

if (config.read_config('module.tx.refresh_login.enable')):
    scheduler.append('qqmusic_refresh_login', refresh,
                     config.read_config('module.tx.refresh_login.interval'))
