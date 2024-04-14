# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: config.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

import ujson as json
import time
import os
import traceback
import sys
import sqlite3
import shutil
import ruamel.yaml as yaml
from . import variable
from .log import log
from . import default_config
import threading

logger = log('config_manager')

# 创建线程本地存储对象
local_data = threading.local()

def get_data_connection():
    # 检查线程本地存储对象是否存在连接对象，如果不存在则创建一个新的连接对象
    if (not hasattr(local_data, 'connection')):
        local_data.connection = sqlite3.connect('./config/data.db')
    return local_data.connection


# 创建线程本地存储对象
local_cache = threading.local()


def get_cache_connection():
    # 检查线程本地存储对象是否存在连接对象，如果不存在则创建一个新的连接对象
    if not hasattr(local_cache, 'connection'):
        local_cache.connection = sqlite3.connect('./cache.db')
    return local_cache.connection


class ConfigReadException(Exception):
    pass


default_str = default_config.default
default = yaml.safe_load(default_str)


def handle_default_config():
    with open("./config/config.yml", "w", encoding="utf-8") as f:
        f.write(default_str)
        if (not os.getenv('build')):
            logger.info('首次启动或配置文件被删除，已创建默认配置文件')
            logger.info(
                f'\n建议您到{variable.workdir + os.path.sep}config.yml修改配置后重新启动服务器')
        return default


class ConfigReadException(Exception):
    pass


def load_data():
    config_data = {}
    try:
        # Connect to the database
        conn = get_data_connection()
        cursor = conn.cursor()

        # Retrieve all configuration data from the 'config' table
        cursor.execute("SELECT key, value FROM data")
        rows = cursor.fetchall()

        for row in rows:
            key, value = row
            config_data[key] = json.loads(value)

    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        logger.error(traceback.format_exc())

    return config_data


def save_data(config_data):
    try:
        # Connect to the database
        conn = get_data_connection()
        cursor = conn.cursor()

        # Clear existing data in the 'data' table
        cursor.execute("DELETE FROM data")

        # Insert the new configuration data into the 'data' table
        for key, value in config_data.items():
            cursor.execute(
                "INSERT INTO data (key, value) VALUES (?, ?)", (key, json.dumps(value)))

        conn.commit()

    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")
        logger.error(traceback.format_exc())


def getCache(module, key):
    try:
        # 连接到数据库（如果数据库不存在，则会自动创建）
        conn = get_cache_connection()

        # 创建一个游标对象
        cursor = conn.cursor()

        cursor.execute("SELECT data FROM cache WHERE module=? AND key=?",
                       (module, key))

        result = cursor.fetchone()
        if result:
            cache_data = json.loads(result[0])
            cache_data["time"] = int(cache_data["time"])
            if (not cache_data['expire']):
                return cache_data
            if (int(time.time()) < int(cache_data['time'])):
                return cache_data
    except:
        pass
        # traceback.print_exc()
    return False


def updateCache(module, key, data):
    try:
        # 连接到数据库（如果数据库不存在，则会自动创建）
        conn = get_cache_connection()

        # 创建一个游标对象
        cursor = conn.cursor()

        cursor.execute(
            "SELECT data FROM cache WHERE module=? AND key=?", (module, key))
        result = cursor.fetchone()
        if result:
            cursor.execute(
                "UPDATE cache SET data = ? WHERE module = ? AND key = ?", (json.dumps(data), module, key))
        else:
            cursor.execute(
                "INSERT INTO cache (module, key, data) VALUES (?, ?, ?)", (module, key, json.dumps(data)))
        conn.commit()
    except:
        logger.error('缓存写入遇到错误…')
        logger.error(traceback.format_exc())


def resetRequestTime(ip):
    config_data = load_data()
    try:
        try:
            config_data['requestTime'][ip] = 0
        except KeyError:
            config_data['requestTime'] = {}
            config_data['requestTime'][ip] = 0
        save_data(config_data)
    except:
        logger.error('配置写入遇到错误…')
        logger.error(traceback.format_exc())


def updateRequestTime(ip):
    try:
        config_data = load_data()
        try:
            config_data['requestTime'][ip] = time.time()
        except KeyError:
            config_data['requestTime'] = {}
            config_data['requestTime'][ip] = time.time()
        save_data(config_data)
    except:
        logger.error('配置写入遇到错误...')
        logger.error(traceback.format_exc())


def getRequestTime(ip):
    config_data = load_data()
    try:
        value = config_data['requestTime'][ip]
    except:
        value = 0
    return value


def read_data(key):
    config = load_data()
    keys = key.split('.')
    value = config
    for k in keys:
        if k not in value and keys.index(k) != len(keys) - 1:
            value[k] = {}
        elif k not in value and keys.index(k) == len(keys) - 1:
            value = None
        value = value[k]

    return value


def write_data(key, value):
    config = load_data()

    keys = key.split('.')
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    current[keys[-1]] = value

    save_data(config)


def push_to_list(key, obj):
    config = load_data()

    keys = key.split('.')
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    if keys[-1] not in current:
        current[keys[-1]] = []

    current[keys[-1]].append(obj)

    save_data(config)


def write_config(key, value):
    config = None
    with open('./config/config.yml', 'r', encoding='utf-8') as f:
        config = yaml.YAML().load(f)

    keys = key.split('.')
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    current[keys[-1]] = value

    # 设置保留注释和空行的参数
    y = yaml.YAML()
    y.preserve_quotes = True
    y.preserve_blank_lines = True

    # 写入配置并保留注释和空行
    with open('./config/config.yml', 'w', encoding='utf-8') as f:
        y.dump(config, f)


def read_default_config(key):
    try:
        config = default
        keys = key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict):
                if k not in value and keys.index(k) != len(keys) - 1:
                    value[k] = {}
                elif k not in value and keys.index(k) == len(keys) - 1:
                    value = None
                value = value[k]
            else:
                value = None
                break

        return value
    except:
        return None


def _read_config(key):
    try:
        config = variable.config
        keys = key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict):
                if k not in value and keys.index(k) != len(keys) - 1:
                    value[k] = None
                elif k not in value and keys.index(k) == len(keys) - 1:
                    value = None
                value = value[k]
            else:
                value = None
                break

        return value
    except (KeyError, TypeError):
        return None


def read_config(key):
    try:
        config = variable.config
        keys = key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict):
                if k not in value and keys.index(k) != len(keys) - 1:
                    value[k] = {}
                elif k not in value and keys.index(k) == len(keys) - 1:
                    value = None
                value = value[k]
            else:
                value = None
                break

        return value
    except:
        default_value = read_default_config(key)
        if (isinstance(default_value, type(None))):
            logger.warning(f'配置文件{key}不存在')
        else:
            for i in range(len(keys)):
                tk = '.'.join(keys[:(i + 1)])
                tkvalue = _read_config(tk)
                logger.debug(f'configfix: 读取配置文件{tk}的值：{tkvalue}')
                if ((tkvalue is None) or (tkvalue == {})):
                    write_config(tk, read_default_config(tk))
                    logger.info(f'配置文件{tk}不存在，已创建')
                    return default_value


def write_data(key, value):
    config = load_data()

    keys = key.split('.')
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    current[keys[-1]] = value

    save_data(config)


def initConfig():
    if (not os.path.exists('./config')):
        os.mkdir('config')
        if (os.path.exists('./config.json')):
            shutil.move('config.json','./config')
        if (os.path.exists('./data.db')):
            shutil.move('./data.db','./config')
        if (os.path.exists('./config/config.json')):
            os.rename('./config/config.json', './config/config.json.bak')
            handle_default_config()
            logger.warning('json配置文件已不再使用，已将其重命名为config.json.bak')
            logger.warning('配置文件不会自动更新（因为变化太大），请手动修改配置文件重启服务器')
            sys.exit(0)

    try:
        with open("./config/config.yml", "r", encoding="utf-8") as f:
            try:
                variable.config = yaml.safe_load(f.read())
                if (not isinstance(variable.config, dict)):
                    logger.warning('配置文件并不是一个有效的字典，使用默认值')
                    variable.config = default
                    with open("./config/config.yml", "w", encoding="utf-8") as f:
                        yaml.dump(variable.config, f)
                        f.close()
            except:
                if os.path.getsize("./config/config.yml") != 0:
                    logger.error("配置文件加载失败，请检查是否遵循YAML语法规范")
                    sys.exit(1)
                else:
                    variable.config = handle_default_config()
    except FileNotFoundError:
        variable.config = handle_default_config()
    # print(variable.config)
    variable.log_length_limit = read_config('common.log_length_limit')
    variable.debug_mode = read_config('common.debug_mode')
    logger.debug("配置文件加载成功")
    conn = sqlite3.connect('./cache.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    # 创建一个表来存储缓存数据
    cursor.execute('''CREATE TABLE IF NOT EXISTS cache
(id INTEGER PRIMARY KEY AUTOINCREMENT,
module TEXT NOT NULL,
key TEXT NOT NULL,
data TEXT NOT NULL)''')

    conn.close()

    conn2 = sqlite3.connect('./config/data.db')

    # 创建一个游标对象
    cursor2 = conn2.cursor()

    cursor2.execute('''CREATE TABLE IF NOT EXISTS data
(key TEXT PRIMARY KEY,
value TEXT)''')

    conn2.close()

    logger.debug('数据库初始化成功')

    # handle data
    all_data_keys = {'banList': [], 'requestTime': {}, 'banListRaw': []}
    data = load_data()
    if (data == {}):
        write_data('banList', [])
        write_data('requestTime', {})
        logger.info('数据库内容为空，已写入默认值')
    for k, v in all_data_keys.items():
        if (k not in data):
            write_data(k, v)
            logger.info(f'数据库中不存在{k}，已创建')

    # 处理代理配置
    if (read_config('common.proxy.enable')):
        if (read_config('common.proxy.http_value')):
            os.environ['http_proxy'] = read_config('common.proxy.http_value')
            logger.info('HTTP协议代理地址: ' +
                        read_config('common.proxy.http_value'))
        if (read_config('common.proxy.https_value')):
            os.environ['https_proxy'] = read_config('common.proxy.https_value')
            logger.info('HTTPS协议代理地址: ' +
                        read_config('common.proxy.https_value'))
        logger.info('代理功能已开启，请确保代理地址正确，否则无法连接网络')

    # cookie池
    if (read_config('common.cookiepool')):
        logger.info('已启用cookie池功能，请确定配置的cookie都能正确获取链接')
        logger.info('传统的源 - 单用户cookie配置将被忽略')
        logger.info('所以即使某个源你只有一个cookie，也请填写到cookiepool对应的源中，否则将无法使用该cookie')
        variable.use_cookie_pool = True

    # 移除已经过期的封禁数据
    banlist = read_data('banList')
    banlistRaw = read_data('banListRaw')
    count = 0
    for b in banlist:
        if (b['expire'] and (time.time() > b['expire_time'])):
            count += 1
            banlist.remove(b)
            if (b['ip'] in banlistRaw):
                banlistRaw.remove(b['ip'])
    write_data('banList', banlist)
    write_data('banListRaw', banlistRaw)
    if (count != 0):
        logger.info(f'已移除{count}条过期封禁数据')

    # 处理旧版数据库的banListRaw
    banlist = read_data('banList')
    banlistRaw = read_data('banListRaw')
    if (banlist != [] and banlistRaw == []):
        for b in banlist:
            banlistRaw.append(b['ip'])
    return


def ban_ip(ip_addr, ban_time=-1):
    if read_config('security.banlist.enable'):
        banList = read_data('banList')
        banList.append({
            'ip': ip_addr,
            'expire': read_config('security.banlist.expire.enable'),
            'expire_time': read_config('security.banlist.expire.length') if (ban_time == -1) else ban_time,
        })
        write_data('banList', banList)
        banListRaw = read_data('banListRaw')
        if (ip_addr not in banListRaw):
            banListRaw.append(ip_addr)
            write_data('banListRaw', banListRaw)
    else:
        if (variable.banList_suggest < 10):
            variable.banList_suggest += 1
            logger.warning('黑名单功能已被关闭，我们墙裂建议你开启这个功能以防止恶意请求')


def check_ip_banned(ip_addr):
    if read_config('security.banlist.enable'):
        banList = read_data('banList')
        banlistRaw = read_data('banListRaw')
        if (ip_addr in banlistRaw):
            for b in banList:
                if (b['ip'] == ip_addr):
                    if (b['expire']):
                        if (b['expire_time'] > int(time.time())):
                            return True
                        else:
                            banList.remove(b)
                            banlistRaw.remove(b['ip'])
                            write_data('banListRaw', banlistRaw)
                            write_data('banList', banList)
                            return False
                    else:
                        return True
                else:
                    return False
            return False
        else:
            return False
    else:
        if (variable.banList_suggest <= 10):
            variable.banList_suggest += 1
            logger.warning('黑名单功能已被关闭，我们墙裂建议你开启这个功能以防止恶意请求')
        return False


initConfig()
