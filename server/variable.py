import os
import aiohttp
from utils import orjson


def _ReadConfig_file():
    try:
        with open("./data/config.json", "r", encoding="utf-8") as f:
            return orjson.load(f)
    except:
        return {}


def _ReadConfig(key):
    try:
        config = _ReadConfig_file()
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


_dm: bool = _ReadConfig("server.debug")
_lm: bool = _ReadConfig("server.output_logs")
debug: bool = (
    True if (os.getenv("CURRENT_ENV") == "development") else (_dm if (_dm) else False)
)
output_logs: bool = _lm if (isinstance(_lm, bool)) else True
running: bool = True
work_dir = os.getcwd()
http_client: aiohttp.ClientSession = None
log_files: list = []
