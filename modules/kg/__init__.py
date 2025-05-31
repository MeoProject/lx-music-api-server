from .lyric import getLyric
from .lyric import lyricSearchByHash
from . import refresh
from .player import url


async def lyric(hash_):
    lyric_search_result = await lyricSearchByHash(hash_)
    choosed_lyric = lyric_search_result[0]
    return await getLyric(choosed_lyric["id"], choosed_lyric["accesskey"])


async def search(query_keywords: str, pages: int, limit: int):
    return await search(query_keywords, pages, limit)
