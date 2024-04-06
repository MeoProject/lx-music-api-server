# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq - (feat. Huibq)
# - name: refresh_token.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
import time
from common import variable
from common import scheduler
from common import config
from common import log
from .utils import signRequest, tools, aes_sign
import ujson as json

logger = log.log('kg_refresh_token')


async def refresh():
    if (not config.read_config('module.kg.user.token')):
        return
    if (not config.read_config('module.kg.user.refresh_token.enable')):
        return
    if (config.read_config('module.kg.client.appid') == '1005'):
        ts = int(time.time() * 1000)
        p3 = aes_sign(json.dumps({'clienttime': ts // 1000, 'token': config.read_config('module.kg.user.token')}))
        data = {
            'p3': p3,
            'clienttime_ms': ts,
            't1': 0,
            't2': 0,
            'userid': config.read_config('module.kg.user.userid')
        }
        params = {
            'dfid': '-',
            'appid': tools.appid,
            'mid': tools.mid,
            'clientver': tools.clientver,
            'clienttime': ts // 1000
        }
        headers = {
            'User-Agent': 'Android712-AndroidPhone-8983-18-0-NetMusic-wifi',
            'KG-THash': '3e5ec6b',
            'KG-Rec': '1',
            'KG-RC': '1',
        }
        login_url = config.read_config('module.kg.user.refresh_token.login_url')
        req = await signRequest(login_url, params, {'method': 'POST', 'json': data, 'headers': headers})
        body = req.json()
        if body['error_code'] != 0:
            logger.warning('刷新登录失败, code: ' +
                           str(body['error_code']) + f'\n响应体: {body}')
            return
        else:
            logger.info('刷新登录成功')
            config.write_config('module.kg.user.userid',
                                str(body['data']['userid']))
            logger.info(f'已通过相应数据更新userid')
            config.write_config('module.kg.user.token',
                                body['data']['token'])
            logger.info('已通过相应数据更新kg_token')
    elif (config.read_config('module.kg.client.appid') == '3116'):
        ts = int(time.time() * 1000)
        p3 = aes_sign(json.dumps({'clienttime': ts // 1000, 'token': config.read_config('module.kg.user.token')}), key=b'c24f74ca2820225badc01946dba4fdf7', iv=b'adc01946dba4fdf7')
        data = {
            'p3': p3,
            'clienttime_ms': ts,
            't1': 0,
            't2': 0,
            'userid': config.read_config('module.kg.user.userid')
        }
        params = {
            'dfid': '-',
            'appid': tools.appid,
            'mid': tools.mid,
            'clientver': tools.clientver,
            'clienttime': ts // 1000
        }
        headers = {
            'User-Agent': 'Android712-AndroidPhone-8983-18-0-NetMusic-wifi',
            'KG-THash': '3e5ec6b',
            'KG-Rec': '1',
            'KG-RC': '1',
        }
        login_url = config.read_config('module.kg.user.refresh_token.login_url')
        req = await signRequest(login_url, params, {'method': 'POST', 'json': data, 'headers': headers})
        body = req.json()
        if body['error_code'] != 0:
            logger.warning('刷新登录失败, code: ' +
                           str(body['error_code']) + f'\n响应体: {body}')
            return
        else:
            logger.info('刷新登录成功')
            config.write_config('module.kg.user.userid',
                                str(body['data']['userid']))
            logger.info(f'已通过相应数据更新userid')
            config.write_config('module.kg.user.token',
                                body['data']['token'])
            logger.info('已通过相应数据更新kg_token')

if (not variable.use_cookie_pool):
    kgconfig = config.read_config('module.kg')
    refresh_login_info = kgconfig.get('refresh_token')
    if (refresh_login_info):
        kgconfig['user']['refresh_token'] = refresh_login_info
        kgconfig.pop('refresh_login')
        config.write_config('module.kg', kgconfig)

if (config.read_config('module.kg.user.refresh_token.enable') and not variable.use_cookie_pool):
    scheduler.append('kg_refresh_token', refresh,
                     config.read_config('module.kg.user.refresh_token.interval'))

async def refresh_login_for_pool(user_info):
    # TODO
    pass

def reg_refresh_login_pool_task():
    # TODO
    pass

if (variable.use_cookie_pool):
    # TODO
    pass
