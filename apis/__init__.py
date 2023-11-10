# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: __init__.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you konw what you are doing.

from common.utils import require
from common.exceptions import FailedException
from common import log
from common import config
from . import kw
from . import mg
from . import kg
from . import tx
from . import wy
import traceback
import time

logger = log.log('api_handler')

sourceExpirationTime = {
    'tx': {
        "expire": True,
        "time": 15 * 60 * 60,  # 15 hours
    },
    'kg': {
        "expire": True,
        "time": 15 * 60 * 60,  # 15 hours
    },
    'kw': {
        "expire": True,
        "time": 30 * 60  # 30 minutes
    },
    'wy': {
        "expire": True,
        "time": 10 * 60,  # 10 minutes
    },
    'mg': {
        # no expiration
        "expire": False,
        "time": 0,
    }

}


async def SongURL(source, songId, quality):
    try:
        c = config.getCache('urls', f'{source}_{songId}_{quality}')
        if c:
            logger.debug(f'使用缓存的{source}_{songId}_{quality}数据，URL：{c["url"]}')
            return {
                'code': 0,
                'msg': 'success',
                'data': c['url'],
            }
    except:
        traceback.print_exc()
    func = require('apis.' + source).url
    try:
        url = await func(songId, quality)
        logger.debug(f'获取{source}_{songId}_{quality}成功，URL：{url}')
        config.updateCache('urls', f'{source}_{songId}_{quality}', {
            "expire": sourceExpirationTime[source]['expire'],
            "time": sourceExpirationTime[source]['time'] + int(time.time()),
            "url": url,
            })
        logger.debug(f'缓存已更新：{source}_{songId}_{quality}, URL：{url}, expire: {sourceExpirationTime[source]["time"] + int(time.time())}')
        return {
            'code': 0,
            'msg': 'success',
            'data': url,
        }
    except FailedException as e:
        return {
            'code': 2,
            'msg': e.args[0],
            'data': None,
        }
