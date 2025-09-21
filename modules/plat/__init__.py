from . import mg
from . import kg
from . import tx
from . import wy


def formatSinger(singerList: list):
    n = []
    for s in singerList:
        n.append(s["name"])
    return "、".join(n)


def numFix(n: int) -> str:
    return f"0{n}" if n < 10 else str(n)


def formatPlayTime(time_seconds: int) -> str:
    minutes = int(time_seconds // 60)
    seconds = int(time_seconds % 60)

    if minutes == 0 and seconds == 0:
        return "--/--"

    return f"{numFix(minutes)}:{numFix(seconds)}"
