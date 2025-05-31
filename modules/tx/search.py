from .utils import signRequest
from common.exceptions import FailedException


async def search(query, page=1, size=50):
    requestBody = {
        "comm": {"ct": "19", "cv": "2102"},
        "req": {
            "method": "DoSearchForQQMusicDesktop",
            "module": "music.search.SearchCgiService",
            "param": {
                "grp": 1,
                "num_per_page": size,
                "page_num": page,
                "query": query,
                "remoteplace": "txt.newclient.top",
                "search_type": 0,
            },
        },
    }
    req = await signRequest(requestBody)
    body = req.json()
    if (body["code"]) or (body["req"]["code"]) != 0:
        raise FailedException("搜索失败")
    return {
        "total": body["req"]["data"]["meta"]["estimate_sum"],
        "page": page,
        "size": size,
        "list": body["req"]["data"]["body"]["song"]["list"],
    }
