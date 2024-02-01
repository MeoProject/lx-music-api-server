# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: lite_signin.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common.exceptions import FailedException
from .utils import buildRequestParams, sign
from common import Httpx, config, utils, variable, scheduler, log
import random
import binascii
import time

logger = log.log('kugou_lite_sign_in')


async def randomMixSongMid(): 
    '''
    通过TOP500榜单获取随机歌曲的mixsongmid
    '''
    # 声明榜单url
    rankUrl = 'http://mobilecdnbj.kugou.com/api/v3/rank/song?version=9108&ranktype=1&plat=0&pagesize=100&area_code=1&page=1&rankid=8888&with_res_tag=0&show_portrait_mv=1'
    # 请求
    res = await Httpx.AsyncRequest(rankUrl, {
        "method": 'GET'
    })
    data = res.json()
    if (data.get('status') != 1):
        raise FailedException('排行榜获取失败')

    # 随机选择一首歌曲
    randomSong = random.choice(data['data']['info'])

    # 因为排行榜api不会返回mixsongmid
    # 所以需要进行一次搜索接口来获取
    search_req = await Httpx.AsyncRequest(utils.encodeURI(f'https://songsearch.kugou.com/song_search_v2?' + buildRequestParams({
        "keyword": randomSong['filename'],
        "area_code": 1,
        "page": 1,
        "pagesize": 1,
        "userid": 0,
        "clientver": "",
        "platform": "WebFilter",
        "filter": 2,
        "iscorrection": 1,
        "privilege_filter": 0
    })), {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36",
            "Referer": "https://www.kugou.com",
        }
    })

    body = search_req.json()

    if (body.get('status') != 1):
        raise FailedException('歌曲搜索失败')
    if (body['data']['total'] == 0 or body['data']['lists'] == []):
        raise FailedException('歌曲搜索失败')

    return body['data']['lists'][0]['MixSongID']


async def do_account_signin(user_info):
    '''
    签到主函数，传入userinfo，响应None就是成功，报错即为不成功
    '''
    # 检查用户配置文件，获取mixsongmid
    mixid = user_info['lite_sign_in']['mixsongmid']['value']
    if (mixid == 'auto'):
        mixid = await randomMixSongMid()
    
    # 声明变量
    headers = {
        'User-Agent': f'Android712-AndroidPhone-{config.read_config("module.kg.client.clientver")}-18-0-NetMusic-wifi',
        'KG-THash': '3e5ec6b',
        'KG-Rec': '1',
        'KG-RC': '1',
        "x-router": "youth.kugou.com"
    }
    body = """{"mixsongid":__id__}""".replace("__id__", str(mixid))

    # params = "userid={}&token={}&appid=3116&clientver=10518&clienttime={}&mid={}&uuid={}&dfid=-".format(read_config("common.kg.userid"), read_config("common.kg.token"), int(time.time()), read_config("common.kg.mid"), str(binascii.hexlify(random.randbytes(16)), encoding = "utf-8"))
    params = {
        "userid": user_info['userid'],
        "token": user_info['token'],
        "appid": 3116,
        "clientver": config.read_config('module.kg.client.clientver'),
        "clienttime": int(time.time()),
        "mid": user_info['mid'],
        "uuid": str(binascii.hexlify(random.randbytes(16)), encoding="utf-8"),
        "dfid": "-"
    }

    params['signature'] = sign(
        params, body, config.read_config('module.kg.client.signatureKey'))

    # 发送请求
    req = await Httpx.AsyncRequest(f"https://gateway.kugou.com/v2/report/listen_song?" +
                                   buildRequestParams(params), {
                                       "method": "POST",
                                       "body": body,
                                       "headers": headers
                                   })
    req = req.json()

    if req['status'] == 1:
        return
    else:
        raise FailedException(req['error_msg'])


def task_handler():
    # not lite client configure
    if (int(config.read_config('module.kg.client.appid')) != 3116):
        return

    # no user
    if ((not variable.use_cookie_pool) and (not config.read_config('module.kg.user.token'))):
        return

    # devide cookiepool
    if (variable.use_cookie_pool):
        pool = config.read_config('module.cookiepool.kg')
        for user in pool:
            index = pool.index(user)
            if (user.get('lite_sign_in') is None):
                user['lite_sign_in'] = {
                    "desc": "是否启用概念版自动签到，仅在appid=3116时运行",
                    "enable": False,
                    "interval": 86400,
                    "mixsongmid": {
                        "desc": "mix_songmid的获取方式, 默认auto, 可以改成一个数字手动",
                        "value": "auto"
                    }
                }
                pool[index] = user
                config.write_config('module.cookiepool.kg', pool)
                logger.info(f'用户池用户(index = {index})配置缺失lite_sign_in字段，已自动写入')
            
        # refresh
        pool = config.read_config('module.cookiepool.kg')
        # add signin schedule task
        for user in pool:
            if (user.get('lite_sign_in').get('enable')):
                scheduler.append(f'kugou_lite_sign_in_{user["userid"]}', do_account_signin, user['lite_sign_in']['interval'], {'user_info': user})
    else:
        user_info = config.read_config('module.kg.user')
        if (user_info.get('lite_sign_in') is None):
            user_info['lite_sign_in'] = {
                "desc": "是否启用概念版自动签到，仅在appid=3116时运行",
                "enable": False,
                "interval": 86400,
                "mixsongmid": {
                    "desc": "mix_songmid的获取方式, 默认auto, 可以改成一个数字手动",
                    "value": "auto"
                }
            }
            config.write_config('module.kg.user', user_info)
            logger.info('用户配置缺失lite_sign_in字段，已自动写入')
        
        if (user_info.get('lite_sign_in').get('enable')):
            scheduler.append(f'kugou_lite_sign_in', do_account_signin, user_info['lite_sign_in']['interval'], {'user_info': user_info})

task_handler()
