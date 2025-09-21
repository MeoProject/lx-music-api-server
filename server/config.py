import os
import sys
import redis
import ujson
from utils import log
from . import variable
from . import default
from .exceptions import (
    ConfigWriteException,
    ConfigReadException,
    ConfigGenerateException,
)
from .exceptions import CacheReadException, CacheWriteException, CacheDeleteException


class ConfigManager:
    def __init__(self):
        self.logger = log.createLogger("Config")
        self.config = {}

        os.makedirs("./data", mode=511, exist_ok=True)

        self.generate()
        self.initConfig()

        self.logger.info("已初始化配置管理器")

    def initConfig(self):
        try:
            with open("./data/config.json", "r", encoding="utf-8") as f:
                self.config = ujson.load(f)
        except FileNotFoundError:
            self.config = default.default

        self.logger.info("配置文件加载成功")

    def generate(self):
        if not os.path.exists("./data/config.json"):
            try:
                with open("./data/config.json", "w", encoding="utf-8") as f:
                    ujson.dump(
                        default.default,
                        f,
                        indent=2,
                        ensure_ascii=False,
                        escape_forward_slashes=False,
                    )
                    f.close()
                    if not os.getenv("build"):
                        self.logger.warning(
                            "首次启动或配置文件被删除，已创建默认配置文件"
                        )
                        self.logger.warning(
                            f"\n建议您到{variable.work_dir + os.path.sep}config.json修改配置后重新启动服务器"
                        )
                    os._exit(1)
            except BaseException as e:
                self.logger.error("配置生成异常...")
                raise ConfigGenerateException(e)

    def read(self, key) -> str | dict | list | None:
        try:
            config = self.config
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
        except BaseException as e:
            self.logger.error("配置读取失败...")
            raise ConfigReadException(e)

    def write(self, key: str, value: str | dict | list):
        try:
            with open("./data/config.json", "r", encoding="utf-8") as f:
                config = ujson.load(f)

            keys = key.split(".")
            current = config
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]

            current[keys[-1]] = value
            self.config = config

            with open("./data/config.json", "w", encoding="utf-8") as f:
                ujson.dump(
                    config,
                    f,
                    indent=2,
                    ensure_ascii=False,
                    escape_forward_slashes=False,
                )
                f.close()
        except BaseException as e:
            self.logger.error("配置写入失败...")
            raise ConfigWriteException(e)


config = ConfigManager()


class CacheManager:
    def __init__(self):
        self.logger = log.createLogger("Cache")
        self.redis = self.connect()
        self.logger.info("已初始化缓存管理器")

    def connect(self):
        try:
            host = config.read("cache.host")
            port = config.read("cache.port")
            user = config.read("cache.user")
            password = config.read("cache.password")
            db = config.read("cache.db")
            client = redis.Redis(
                host=host, port=port, username=user, password=password, db=db
            )
            if not client.ping():
                raise
            return client
        except Exception as e:
            self.logger.error(f"连接Redis缓存数据库失败: {e}")
            sys.exit(1)

    def buildKey(self, module: str, key: str):
        prefix = config.read("cache.key_prefix")
        return f"{prefix}:{module}:{key}"

    def get(self, module: str, key: str):
        try:
            key = self.buildKey(module, key)
            result = self.redis.get(key)
            if result:
                cache_data = ujson.loads(result)
                return cache_data
        except BaseException as e:
            self.logger.error("缓存读取遇到错误…")
            raise CacheReadException(e)

    def set(self, module: str, key: str, data: str | dict | list, expire: int = None):
        try:
            key = self.buildKey(module, key)
            self.redis.set(
                key, ujson.dumps(data), ex=expire if expire and expire > 0 else None
            )
        except BaseException as e:
            self.logger.error("缓存写入遇到错误…")
            raise CacheWriteException(e)

    def delete(self, module: str, key: str):
        try:
            key = self.buildKey(module, key)
            self.redis.delete(key)
        except BaseException as e:
            self.logger.error("缓存删除遇到错误…")
            raise CacheDeleteException(e)


cache = None

if config.read("cache.enable"):
    cache = CacheManager()
