# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: Httpx.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

import aiohttp
# import asyncio
import requests
import random
import traceback
import zlib
import ujson as json
import re
import time
import pickle
from . import log
from . import config
from . import utils
from . import variable

def is_valid_utf8(text):
    try:
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        # 判断是否为有效的utf-8字符串
        if "\ufffe" in text:
            return False
        try:
            text.encode('utf-8').decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
    except:
        logger.error(traceback.format_exc())
        return False

def is_plain_text(text):
    # 判断是否为纯文本
    pattern = re.compile(r'[^\x00-\x7F]')
    return not bool(pattern.search(text))

def convert_dict_to_form_string(dic):
    # 将字典转换为表单字符串
    return '&'.join([f'{k}={v}' for k, v in dic.items()])

def log_plaintext(text):
    if (text.startswith('{') and text.endswith('}')):
        try:
            text = json.loads(text)
        except:
            pass
    elif (text.startswith('<xml') and text.endswith('>')): # xml data
        try:
            text = f'xml: {utils.load_xml(text)}'
        except:
            pass
    return text

# 内置的UA列表
ua_list = [ 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0  uacq',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5666.197 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 uacq',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
            ]

# 日志记录器
logger = log.log('http_utils')

def request(url, options = {}):
    '''
    Http请求主函数, 用于发送网络请求
    - url: 需要请求的URL地址(必填)
    - options: 请求的配置参数(可选, 留空时为GET请求, 总体与nodejs的请求的options填写差不多)
        - method: 请求方法
        - headers: 请求头
        - body: 请求体(也可使用python原生requests库的data参数)
        - form: 提交的表单数据
        - cache: 缓存设置
                - no-cache: 不缓存
                - <int>: 缓存可用秒数
        - cache-ignore: <list> 缓存忽略关键字
    
    @ return: requests.Response类型的响应数据
    '''
    # 缓存读取
    cache_key = f'{url}{options}'
    if (isinstance(options.get('cache-ignore'), list)):
        for i in options.get('cache-ignore'):
            cache_key = cache_key.replace(str(i), '')
        options.pop('cache-ignore')
    cache_key = utils.createMD5(cache_key)
    if options.get("cache") and options["cache"] != "no-cache":
        cache = config.getCache("httpx", cache_key)
        if cache:
            logger.debug(f"请求 {url} 有可用缓存")
            return pickle.loads(utils.createBase64Decode(cache["data"]))
    if "cache" in list(options.keys()):
        cache_info = options.get("cache")
        options.pop("cache")
    else:
        cache_info = None
    

    # 获取请求方法，没有则默认为GET请求
    try:
        method = options['method']
        options.pop('method')
    except Exception as e:
        method = 'GET'
    # 获取User-Agent，没有则从ua_list中随机选择一个
    try:
        d_lower = {k.lower(): v for k, v in options['headers'].items()}
        useragent = d_lower['user-agent']
    except:
        try:
            options['headers']['User-Agent'] = random.choice(ua_list)
        except:
            options['headers'] = {}
            options['headers']['User-Agent'] = random.choice(ua_list)
    # 检查是否在国内
    if ((not variable.iscn) and (not options["headers"].get("X-Forwarded-For"))):
        options["headers"]["X-Forwarded-For"] = variable.fakeip
    # 获取请求主函数
    try:
        reqattr = getattr(requests, method.lower())
    except AttributeError:
        raise AttributeError('Unsupported method: '+method)
    # 请求前记录
    logger.debug(f'HTTP Request: {url}\noptions: {options}')
    # 转换body/form参数为原生的data参数，并为form请求追加Content-Type头
    if (method == 'POST') or (method == 'PUT'):
        if options.get('body'):
            options['data'] = options['body']
            options.pop('body')
        if options.get('form'):
            options['data'] = convert_dict_to_form_string(options['form'])
            options.pop('form')
            options['headers']['Content-Type'] = 'application/x-www-form-urlencoded'
        if (isinstance(options['data'], dict)):
            options['data'] = json.dumps(options['data'])
    # 进行请求
    try:
        logger.info("-----start----- " + url)
        req = reqattr(url, **options)
    except Exception as e:
        logger.error(f'HTTP Request runs into an Error: {log.highlight_error(traceback.format_exc())}')
        raise e
    # 请求后记录
    logger.debug(f'Request to {url} succeed with code {req.status_code}')
    if (req.content.startswith(b'\x78\x9c') or req.content.startswith(b'\x78\x01')): # zlib headers
        try:
            decompressed = zlib.decompress(req.content)
            if (is_valid_utf8(decompressed)):
                logger.debug(log_plaintext(decompressed.decode("utf-8")))
            else:
                logger.debug('response is not text binary, ignore logging it')
        except:
            logger.debug('response is not text binary, ignore logging it')
    else:
        if (is_valid_utf8(req.content)):
            logger.debug(log_plaintext(req.content.decode("utf-8")))
        else:
            logger.debug('response is not text binary, ignore logging it')
    # 缓存写入
    if (cache_info and cache_info != "no-cache"):
        cache_data = pickle.dumps(req)
        expire_time = (cache_info if isinstance(cache_info, int) else 3600) + int(time.time())
        config.updateCache("httpx", cache_key, {"expire": True, "time": expire_time, "data": utils.createBase64Encode(cache_data)})
        logger.debug("缓存已更新: " + url)
    def _json():
        return json.loads(req.content)
    setattr(req, 'json', _json)
    # 返回请求
    return req


def checkcn():
    try:
        req = request("https://mips.kugou.com/check/iscn?&format=json")
        body = utils.CreateObject(req.json())
        variable.iscn = bool(body.flag)
        if (not variable.iscn):
            variable.fakeip = config.read_config('common.fakeip')
            logger.info(f"您在非中国大陆服务器({body.country})上启动了项目，已自动开启ip伪装")
            logger.warning("此方式无法解决咪咕音乐的链接获取问题，您可以配置代理，服务器地址可在下方链接中找到\nhttps://hidemy.io/cn/proxy-list/?country=CN#list")
    except Exception as e:
        logger.warning('检查服务器位置失败，已忽略')
        logger.warning(traceback.format_exc())

class ClientResponse:
    # 这个类为了方便aiohttp响应与requests响应的跨类使用，也为了解决pickle无法缓存的问题
    def __init__(self, status, content, headers):
        self.status = status
        self.content = content
        self.headers = headers
        self.text = content.decode("utf-8", errors='ignore')
    
    def json(self):
        return json.loads(self.content)


async def convert_to_requests_response(aiohttp_response):
    content = await aiohttp_response.content.read()  # 从aiohttp响应中读取字节数据
    status_code = aiohttp_response.status  # 获取状态码
    headers = dict(aiohttp_response.headers.items())  # 获取标头信息并转换为字典
    
    return ClientResponse(status_code, content, headers)

async def AsyncRequest(url, options = {}):
    '''
    Http异步请求主函数, 用于发送网络请求
    - url: 需要请求的URL地址(必填)
    - options: 请求的配置参数(可选, 留空时为GET请求, 总体与nodejs的请求的options填写差不多)
        - method: 请求方法
        - headers: 请求头
        - body: 请求体(也可使用python原生requests库的data参数)
        - form: 提交的表单数据
        - cache: 缓存设置
                - no-cache: 不缓存
                - <int>: 缓存可用秒数
        - cache-ignore: <list> 缓存忽略关键字
    
    @ return: requests.Response类型的响应数据
    '''
    if (not variable.aioSession):
        variable.aioSession = aiohttp.ClientSession()
    # 缓存读取
    cache_key = f'{url}{options}'
    if (isinstance(options.get('cache-ignore'), list)):
        for i in options.get('cache-ignore'):
            cache_key = cache_key.replace(str(i), '')
        options.pop('cache-ignore')
    cache_key = utils.createMD5(cache_key)
    if options.get("cache") and options["cache"] != "no-cache":
        cache = config.getCache("httpx_async", cache_key)
        if cache:
            logger.debug(f"请求 {url} 有可用缓存")
            c = pickle.loads(utils.createBase64Decode(cache["data"]))
            return c
    if "cache" in list(options.keys()):
        cache_info = options.get("cache")
        options.pop("cache")
    else:
        cache_info = None
    

    # 获取请求方法，没有则默认为GET请求
    try:
        method = options['method']
        options.pop('method')
    except Exception as e:
        method = 'GET'
    # 获取User-Agent，没有则从ua_list中随机选择一个
    try:
        d_lower = {k.lower(): v for k, v in options['headers'].items()}
        useragent = d_lower['user-agent']
    except:
        try:
            options['headers']['User-Agent'] = random.choice(ua_list)
        except:
            options['headers'] = {}
            options['headers']['User-Agent'] = random.choice(ua_list)
    # 检查是否在国内
    if ((not variable.iscn) and (not options["headers"].get("X-Forwarded-For"))):
        options["headers"]["X-Forwarded-For"] = variable.fakeip
    # 获取请求主函数
    try:
        reqattr = getattr(variable.aioSession, method.lower())
    except AttributeError:
        raise AttributeError('Unsupported method: '+method)
    # 请求前记录
    logger.debug(f'HTTP Request: {url}\noptions: {options}')
    # 转换body/form参数为原生的data参数，并为form请求追加Content-Type头
    if (method == 'POST') or (method == 'PUT'):
        if options.get('body'):
            options['data'] = options['body']
            options.pop('body')
        if options.get('form'):
            options['data'] = convert_dict_to_form_string(options['form'])
            options.pop('form')
            options['headers']['Content-Type'] = 'application/x-www-form-urlencoded'
        if (isinstance(options['data'], dict)):
            options['data'] = json.dumps(options['data'])
    # 进行请求
    try:
        logger.info("-----start----- " + url)
        req_ = await reqattr(url, **options)
    except Exception as e:
        logger.error(f'HTTP Request runs into an Error: {log.highlight_error(traceback.format_exc())}')
        raise e
    # 请求后记录
    logger.debug(f'Request to {url} succeed with code {req_.status}')
    # 为懒人提供的不用改代码移植的方法
    # 才不是梓澄呢
    req = await convert_to_requests_response(req_)
    if (req.content.startswith(b'\x78\x9c') or req.content.startswith(b'\x78\x01')): # zlib headers
        try:
            decompressed = zlib.decompress(req.content)
            if (is_valid_utf8(decompressed)):
                logger.debug(log_plaintext(decompressed.decode("utf-8")))
            else:
                logger.debug('response is not text binary, ignore logging it')
        except:
            logger.debug('response is not text binary, ignore logging it')
    else:
        if (is_valid_utf8(req.content)):
            logger.debug(log_plaintext(req.content.decode("utf-8")))
        else:
            logger.debug('response is not text binary, ignore logging it')
    # 缓存写入
    if (cache_info and cache_info != "no-cache"):
        cache_data = pickle.dumps(req)
        expire_time = (cache_info if isinstance(cache_info, int) else 3600) + int(time.time())
        config.updateCache("httpx_async", cache_key, {"expire": True, "time": expire_time, "data": utils.createBase64Encode(cache_data)})
        logger.debug("缓存已更新: " + url)
    # 返回请求
    return req