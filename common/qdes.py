import zlib
import binascii

from .log import log
from . import variable

logger = log("QQ Lyric Decoder")

try:
    from .natives import qdes

    variable.QRCDecrypterLoaded = True
except:
    try:
        import qdes

        variable.QRCDecrypterLoaded = True
    except:
        logger.warning(
            "QRC解密库qdes加载失败, 可能为不支持当前系统, QRC相关的逐字歌词获取将无法使用"
        )


def qdes_decrypt(qrc):
    if variable.QRCDecrypterLoaded:
        decoded = zlib.decompress(
            qdes.LyricDecode(binascii.unhexlify(qrc.encode("utf-8")))
        ).decode("utf-8")
        return decoded
    else:
        raise ModuleNotFoundError("qdes解密库未被加载")
