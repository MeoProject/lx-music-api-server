import os as os
import aiohttp
import requests
import ujson as json
from . import stats


def _ReadConfig_file():
    try:
        with open("./data/config.json", "r", encoding="utf-8") as f:
            return json.load(f)
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


_dm: bool = _ReadConfig("common.debug_mode")
_lm: bool = _ReadConfig("common.log_file")

DebugMode: bool = (
    True if (os.getenv("CURRENT_ENV") == "development") else (_dm if (_dm) else False)
)

with open("./package.json", "r", encoding="utf-8") as f:
    PackageInfo: dict = json.loads(f.read())

LogFile: bool = _lm if (isinstance(_lm, bool)) else True
Running: bool = True
Config: dict = {}
WorkDir = os.getcwd()
FakeIP = None
SyncClient: requests.Session = None
AsyncClient: aiohttp.ClientSession = None
QRCDecrypterLoaded: bool = False
LogFiles: list = []
RefreshDone = False
StatsManager = stats.StatisticsManager()
