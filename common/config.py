import os
import sys
import traceback
import ujson as json
import threading
import redis
from typing import Tuple

from . import log
from . import variable
from . import default

from common.exceptions import ConfigReadException, ConfigWriteException


logger = log.log("Config Manager")


Redis = threading.local()


def ConnectToRedis() -> redis.Redis:
    try:
        host = ReadConfig("common.cache.redis.host")
        port = ReadConfig("common.cache.redis.port")
        user = ReadConfig("common.cache.redis.user")
        password = ReadConfig("common.cache.redis.password")
        db = ReadConfig("common.cache.redis.db")

        client = redis.Redis(
            host=host, port=port, username=user, password=password, db=db
        )
        if not client.ping():
            raise
        Redis = client
        return Redis
    except Exception as e:
        logger.error(f"连接Redis缓存数据库失败: {e}")
        sys.exit(1)


def InitDirs():
    names = ["./data", "./data/script", "./data/ssl", "./data/gcsp", "./data/musicfree"]
    for name in names:
        try:
            os.makedirs(name, mode=511, exist_ok=True)
            logger.info(f"已创建文件夹：{name}")
        except OSError:
            logger.error(f"创建文件夹失败: {name}")


default = default.default


def HandleDefaultConfig():
    try:
        with open("./data/config.json", "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    default, indent=2, ensure_ascii=False, escape_forward_slashes=False
                )
            )
            f.close()
            if not os.getenv("build"):
                logger.info("首次启动或配置文件被删除，已创建默认配置文件")
                logger.info(
                    f"\n建议您到{variable.WorkDir + os.path.sep}config.json修改配置后重新启动服务器"
                )
            return default
    except Exception as e:
        raise ConfigReadException(e)


def handleBuildRedisKey(module: str, key: str) -> str:
    prefix = ReadConfig("common.cache.redis.key_prefix")
    return f"{prefix}:{module}:{key}"


def GetCache(module: str, key: str) -> dict | None:
    try:
        redis = ConnectToRedis()
        key = handleBuildRedisKey(module, key)
        result = redis.get(key)
        if result:
            cache_data = json.loads(result)
            return cache_data
    except:
        pass
    return None


def UpdateCache(
    module: str, key: str, data: str | dict | list, expire: int = None
) -> None:
    try:
        redis = ConnectToRedis()
        key = handleBuildRedisKey(module, key)
        redis.set(key, json.dumps(data), ex=expire if expire and expire > 0 else None)
    except:
        logger.error("缓存写入遇到错误…")
        logger.error(traceback.format_exc())


def DeleteCache(module: str, key: str) -> None:
    try:
        redis = ConnectToRedis()
        key = handleBuildRedisKey(module, key)
        redis.delete(key)
    except:
        logger.error("缓存删除遇到错误…")
        logger.error(traceback.format_exc())


def BanIP(ip_addr: str) -> bool:
    redis = ConnectToRedis()
    if ReadConfig("security.banlist.enable"):
        # Get the current ban list or create an empty one if it doesn't exist
        ban_list_data = redis.get("IKUN_API:BanList")
        if ban_list_data:
            ban_list: list = json.loads(ban_list_data)
        else:
            ban_list = []

        # Add the IP to the ban list if it's not already there
        if ip_addr not in ban_list:
            ban_list.append(ip_addr)
            redis.set("IKUN_API:BanList", json.dumps(ban_list))
            logger.info(f"已写入黑名单: {ip_addr}")

        return True
    else:
        return False


def CheckIPBanned(ip_addr: str) -> bool:
    redis = ConnectToRedis()
    if ReadConfig("security.banlist.enable"):
        ban_list_data = redis.get("IKUN_API:BanList")
        if ban_list_data:
            ban_list: list = json.loads(ban_list_data)
            return ip_addr in ban_list
        else:
            return False
    else:
        return False


def WriteConfig(key: str, value: str | dict | list) -> None:
    try:
        config = None
        with open("./data/config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        keys = key.split(".")
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        variable.Config = config

        with open("./data/config.json", "w", encoding="utf-8") as f:
            json.dump(
                config, f, indent=2, ensure_ascii=False, escape_forward_slashes=False
            )
            f.close()
    except Exception as e:
        raise ConfigWriteException(e)


def ReadDefaultConfig(key: str) -> dict | list | str | None:
    try:
        config = default
        keys = key.split(".")
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


def _ReadConfig(key: str) -> str | dict | list | None:
    try:
        config = variable.Config
        keys = key.split(".")
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


def ReadConfig(key) -> str | dict | list | None:
    try:
        config = variable.Config
        keys = key.split(".")
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
        default_value = ReadDefaultConfig(key)
        if isinstance(default_value, type(None)):
            logger.warning(f"配置文件{key}不存在")
        else:
            for i in range(len(keys)):
                tk = ".".join(keys[: (i + 1)])
                tkvalue = _ReadConfig(tk)
                logger.info(f"configfix: 读取配置文件{tk}的值：{tkvalue}")
                if (tkvalue is None) or (tkvalue == {}):
                    WriteConfig(tk, ReadDefaultConfig(tk))
                    logger.info(f"配置文件{tk}不存在，已创建")
                    return default_value


def GetKeyInfo(key: str) -> Tuple[bool, bool]:
    key_list = ReadConfig("security.key.list")
    if key in key_list:
        return ReadConfig("security.key.enable"), True
    else:
        return ReadConfig("security.key.enable"), False


def InitConfig():
    InitDirs()

    try:
        with open("./data/config.json", "r", encoding="utf-8") as f:
            try:
                variable.Config = json.loads(f.read())
                if not isinstance(variable.Config, dict):
                    logger.warning("配置文件并不是一个有效的字典，使用默认值")
                    variable.Config = default
                    with open("./data/config.json", "w", encoding="utf-8") as f:
                        f.write(
                            json.dumps(
                                variable.Config,
                                indent=2,
                                ensure_ascii=False,
                                escape_forward_slashes=False,
                            )
                        )
                        f.close()
            except:
                if os.path.getsize("./data/config.json") != 0:
                    logger.error("配置文件加载失败, 请检查是否遵循JSON语法规范")
                    sys.exit(1)
                else:
                    variable.Config = HandleDefaultConfig()
    except FileNotFoundError:
        variable.Config = HandleDefaultConfig()

    if not ConnectToRedis():
        raise Exception("你还没启动Redis数据库")

    variable.DebugMode = ReadConfig("common.debug_mode")
    logger.info("配置文件加载成功")

    if not ReadConfig("common.cache.enable"):
        logger.warning("缓存功能已关闭，我们墙裂建议您开启缓存以防止恶意请求")


InitConfig()
