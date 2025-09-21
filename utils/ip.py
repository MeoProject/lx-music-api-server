import ipaddress
from .http import HttpRequest


async def getIPInfo(ip: str) -> dict:
    try:
        if ip == ("127.0.0.1" or "::1"):
            return {"ip": ip, "local": "本地IP"}

        req = await HttpRequest(
            "https://mips.kugou.com/check/iscn",
            {"method": "GET", "headers": {"X-Forwarded-For": ip}},
        )
        body = req.json()

        if body["errcode"] != 0:
            return {"ip": ip, "local": "获取失败"}

        return {"ip": ip, "local": body["country"]}
    except:
        return {"ip": ip, "local": "获取失败"}


def isLocalIP(ip):
    try:
        i = ipaddress.ip_address(ip)
        return i.is_private
    except:
        return False
