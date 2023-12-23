# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: qdes.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from .log import log
from . import variable
import binascii
import zlib

logger = log('qdes')

try:
    from .natives import qdes
    variable.qdes_lib_loaded = True
except:
    try:
        import qdes
        variable.qdes_lib_loaded = True
    except:
        logger.warning('QRC解密库qdes加载失败, 可能为不支持当前系统, QRC相关的逐字歌词获取将无法使用')

def qdes_decrypt(qrc):
    if variable.qdes_lib_loaded:
        decoded = zlib.decompress(qdes.LyricDecode(binascii.unhexlify(qrc.encode('utf-8')))).decode('utf-8')
        return decoded
    else:
        raise ModuleNotFoundError('qdes解密库未被加载')