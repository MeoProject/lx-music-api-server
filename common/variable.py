# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: variable.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

import os as _os
import ujson as _json

def _read_config_file():
    try:
        with open("./config/config.json", "r", encoding = "utf-8") as f:
            return _json.load(f)
    except:
        return {}

def _read_config(key):
    try:
        config = _read_config_file()
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
_dm = _read_config("common.debug_mode")
_lm = _read_config("common.log_file")
_ll = _read_config("common.log_length_limit")
debug_mode = _dm if (_dm) else False
log_length_limit = _ll if (_ll) else 500
log_file = _lm if (isinstance(_lm , bool)) else True
running = True
config = {}
workdir = _os.getcwd()
banList_suggest = 0
iscn = True
fake_ip = None
aioSession = None
qdes_lib_loaded = False
use_cookie_pool = False
running_ports = []
use_proxy = False
http_proxy = ''
https_proxy = ''
