# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: Httpx.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you know what you are doing.

# import aiohttp
import asyncio
import requests
import random
import traceback
import zlib
import ujson as json
from .log import log
import re
import binascii

def is_valid_utf8(text):
    # 判断是否为有效的utf-8字符串
    if "\ufffe" in text:
        return False
    try:
        text.encode('utf-8').decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

def is_plain_text(text):
    # 判断是否为纯文本
    pattern = re.compile(r'[^\x00-\x7F]')
    return not bool(pattern.search(text))

def convert_dict_to_form_string(dic):
    # 将字典转换为表单字符串
    return '&'.join([f'{k}={v}' for k, v in dic.items()])

# 内置的UA列表
ua_list = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39||Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0||Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0  uacq||Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5666.197 Safari/537.36||Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 uacq||Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'.split('||')

# 日志记录器
logger = log('http_utils')

def request(url, options = {}):
    '''
     - Http请求主函数, 用于发送网络请求
     - url: 需要请求的URL地址(必填)
     - options: 请求的配置参数(可选, 留空时为GET请求, 总体与nodejs的请求的options填写差不多)
       - method: 请求方法
       - headers: 请求头
       - body: 请求体(也可使用python原生requests库的data参数)
       - form: 提交的表单数据
    
     @ return: requests.Response类型的响应数据
    '''
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
    # 进行请求
    try:
        req = reqattr(url, **options)
    except Exception as e:
        logger.error(f'HTTP Request runs into an Error: {traceback.format_exc()}')
        raise e
    # 请求后记录
    logger.debug(f'Request to {url} succeed with code {req.status_code}')
    # 记录响应数据
    try:
        logger.debug(json.loads(req.content.decode("utf-8")))
    except:
        try:
            logger.debug(json.loads(zlib.decompress(req.content).decode("utf-8")))
        except zlib.error:
            if is_valid_utf8(req.text) and is_plain_text(req.text):
                logger.debug(req.text)
            else:
                logger.debug(binascii.hexlify(req.content))
        except:
            logger.debug(zlib.decompress(req.content).decode("utf-8") if is_valid_utf8(zlib.decompress(req.content).decode("utf-8")) and is_plain_text(zlib.decompress(req.content).decode("utf-8")) else binascii.hexlify(zlib.decompress(req.content)))
    # 返回请求
    return req

"""
async def asyncrequest(url, options={}):
    '''
     - Asynchronous HTTP request function used for sending network requests
     - url: URL address to be requested (required)
     - options: Configuration parameters for the request (optional, defaults to GET request)
       - method: Request method
       - headers: Request headers
       - body: Request body (can also use the native 'data' parameter of the 'requests' library)
       - form: Submitted form data
    
     @ return: aiohttp.ClientResponse type response data
    '''
    # Get the request method, defaulting to GET if not provided
    try:
        method = options['method']
        options.pop('method')
    except KeyError:
        method = 'GET'
    # Get the User-Agent, choose randomly from ua_list if not present
    try:
        d_lower = {k.lower(): v for k, v in options['headers'].items()}
        useragent = d_lower['user-agent']
    except KeyError:
        try:
            options['headers']['User-Agent'] = random.choice(ua_list)
        except:
            options['headers'] = {}
            options['headers']['User-Agent'] = random.choice(ua_list)
    # Get the request function
    try:
        reqattr = getattr(aiohttp.ClientSession(), method.lower())
    except AttributeError:
        raise AttributeError('Unsupported method: ' + method)
    # Log before the request
    logger.debug(f'HTTP Request: {url}\noptions: {options}')
    # Convert body/form parameter to native 'data' parameter and add 'Content-Type' header for form requests
    if method in ['POST', 'PUT']:
        if options.get('body'):
            options['data'] = options['body']
            options.pop('body')
        if options.get('form'):
            options['data'] = convert_dict_to_form_string(options['form'])
            options.pop('form')
            options['headers']['Content-Type'] = 'application/x-www-form-urlencoded'
    # Send the request
    try:
        async with reqattr(url, **options) as req:
            res = await req.read()
    except Exception as e:
        logger.error(f'HTTP Request runs into an Error: {traceback.format_exc()}')
        raise e
    # Log after the request
    logger.debug(f'Request to {url} succeed with code {req.status}')
    # Log the response data
    try:
        logger.debug(json.loads(res.decode("utf-8")))
    except:
        try:
            logger.debug(json.loads(zlib.decompress(res).decode("utf-8")))
        except zlib.error:
            if is_valid_utf8(req.text) and is_plain_text(req.text):
                logger.debug(req.text)
            else:
                logger.debug(binascii.hexlify(res))
        except:
            logger.debug(
                zlib.decompress(res).decode("utf-8") if is_valid_utf8(zlib.decompress(res).decode("utf-8")) and is_plain_text(
                    zlib.decompress(res).decode("utf-8")) else binascii.hexlify(zlib.decompress(res)))
    # Return the response
    return req
    
"""