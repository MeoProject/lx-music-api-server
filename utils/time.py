import time


def timeLengthFormat(t: int) -> str:
    try:
        t = int(t)
    except:
        return "//"

    hour = t // 3600
    minute = (t % 3600) // 60
    second = t % 60

    return f"{((('0' + str(hour)) if (len(str(hour)) == 1) else str(hour)) + ':') if (hour > 0) else ''}{minute:02}:{second:02}"


def tsFormat(t: int) -> str:
    if not isinstance(t, int):
        t = int(t)

    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


def getCurrentTimestamp() -> int:
    return int(time.time())
