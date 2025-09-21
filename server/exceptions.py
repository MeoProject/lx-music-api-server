class FailedException(Exception):
    """统一异常"""

    pass


class getUrlFailed(Exception):
    """链接获取失败异常"""

    pass


class getSongInfoFailed(Exception):
    """歌曲详情获取失败异常"""

    pass


class getLyricFailed(Exception):
    """歌词获取失败异常"""

    pass


class ConfigWriteException(Exception):
    """配置写入异常"""

    pass


class ConfigReadException(Exception):
    """配置读取异常"""

    pass


class ConfigGenerateException(Exception):
    """配置生成异常"""

    pass


class CacheWriteException(Exception):
    """缓存写入异常"""

    pass


class CacheReadException(Exception):
    """缓存读取异常"""

    pass


class CacheDeleteException(Exception):
    """缓存删除异常"""

    pass
