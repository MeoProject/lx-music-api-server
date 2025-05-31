from common import request
from urllib.parse import urlparse
from common.exceptions import FailedException
import random
import ipaddress


def is_ip(hostname):
    try:
        ipaddress.ip_address(hostname)
        return True
    except:
        return False


def random_ip():
    ranges = [
        (607649792, 608174079),
        (975044608, 977272831),
        (999751680, 999784447),
        (1019346944, 1019478015),
        (1038614528, 1039007743),
        (1783627776, 1784676351),
        (1947009024, 1947074559),
        (1987051520, 1988034559),
        (2035023872, 2035154943),
        (2078801920, 2079064063),
        (2344878080, 2346188799),
        (2869428224, 2869952511),
        (3058696192, 3059548159),
        (3524853760, 3525359615),
        (3725590528, 3729833983),
    ]
    start, end = random.choice(ranges)
    return ".".join(
        map(
            str,
            [
                (random.randint(start, end) >> 24) & 0xFF,
                (random.randint(start, end) >> 16) & 0xFF,
                (random.randint(start, end) >> 8) & 0xFF,
                random.randint(start, end) & 0xFF,
            ],
        )
    )


async def url(partid: str, quality: str):
    match quality:
        case "720p":
            q = 3
        case "1080p":
            q = 6
        case "4k":
            q = 9
        case _:
            q = 9
    ok_svrip = [
        "pcvideotx.titan.mgtv.com",
        "pcvideotxott.titan.mgtv.com",
        "pcvideoaliyun.titan.mgtv.com",
        "pcvideoaliyunott.titan.mgtv.com",
    ]
    ip = random_ip()
    req = await request.AsyncRequest(
        "http://ott.liveapi.mgtv.com/v1/epg5/getVodPlayUrl?",
        {
            "method": "GET",
            "params": {
                "mod": "DLT-A0",
                "pver": "0|0|0|0|0|0|0|0",
                "channel_code": "DBEI",
                "uuid": "mgtvmac00DBF2E344F8",
                "mac_id": "00-DB-F2-E3-44-F8",
                "platform": "3",
                "mf": "blackshark",
                "part_id": partid,
                "svrip": random.choice(ok_svrip),
                "device_id": "00DBF2E344F800000000000000000000",
                "ticket": "",
                "time_zone": "GMT 08:00",
                "version": "6.3.703.383.3.DBEI_TVAPP.0.0_Release",
                "preview": "2",
                "quality": q,
                "license": "ZgOOgo5MjkyOTAYGKzK4S3qtLS4fAYGBgYGBgYGBgYGBgYGBgo5MjkyOTGDYjoI=",
                "model_code": "DLT-A0",
            },
            "headers": {
                "X-Forwarded-For": ip,
                "Client-IP": ip,
                "X-Real-IP": ip,
                "Origin": "https://www.mgtv.com",
                "Referer": "https://www.mgtv.com",
                "Connection": "Keep-Alive",
                "User-Agent": "ImgoMediaPlayerLib/com.hunantv.imgo.activity.V8.3.6 (Linux;Android 12(32)) mediacodecNative/0/5.11.1_2.25010901.20250110/imgofflib",
            },
        },
    )
    body = req.json()
    if body["errno"] != "0":
        raise FailedException("失败")
    data = body["data"]
    fwl = [
        "slicetx.titan.mgtv.com",
        "sluicetx.titan.mgtv.com",
    ]
    url_parsed = urlparse(data["url"])
    if is_ip(url_parsed.hostname):
        return await url(partid, quality)
    if url_parsed.hostname in fwl:
        return await url(partid, quality)
    if url_parsed.scheme == "http":
        _url = str(data["url"]).replace("http", "https")
    check_req = await request.AsyncRequest(data["url"], {"method": "HEAD"})
    if check_req.status != 200:
        return await url(partid, quality)
    return {"url": _url, "quality": quality}
