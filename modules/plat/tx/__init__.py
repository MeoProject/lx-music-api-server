from . import sign
from . import utils

from typing import Any
from pathlib import Path
from utils import device, qimei


# Build Official Android
async def build_comm(
    user_info: dict | None = None,
) -> dict[str, Any]:
    if user_info:
        DEVICE_PATH = Path(f"data/cache/txo_{user_info['uin']}.json")
    else:
        DEVICE_PATH = Path("data/cache/device.json")

    if not DEVICE_PATH.exists():
        DEVICE = device.Device()
        QIMEI = await qimei.get_qimei("14.9.0.8")
        DEVICE.qimei = QIMEI
        device.save_device(DEVICE, DEVICE_PATH)
    else:
        DEVICE = device.get_cached_device(DEVICE_PATH)
        QIMEI = DEVICE.qimei

    common = {
        "v": 14090008,
        "ct": 11,
        "cv": 14090008,
        "chid": "2005000982",
        "QIMEI": QIMEI["q16"],
        "QIMEI36": QIMEI["q36"],
        "tmeAppID": "qqmusic",
        "format": "json",
        "inCharset": "utf-8",
        "outCharset": "utf-8",
    }
    if user_info is not None and user_info.get("uin") and user_info.get("token"):
        if str(user_info["token"]).startswith("W_X_"):
            tmeLoginType = 1
        else:
            tmeLoginType = 2
        common.update(
            {
                "qq": str(user_info["uin"]),
                "authst": user_info["token"],
                "tmeLoginType": tmeLoginType,
            }
        )
    common.update(
        {
            "OpenUDID": "ffffffffbff94f7d000000000033c587",
            "udid": "ffffffffbff94f7d000000000033c587",
            "os_ver": DEVICE.version.release,
            "aid": "d2550265db4ce5c4",
            "phonetype": DEVICE.model,
            "devicelevel": DEVICE.version.sdk,
            "newdevicelevel": DEVICE.version.sdk,
            "nettype": "1030",
            "rom": DEVICE.fingerprint,
            "OpenUDID2": "ffffffffbff94f7d000001999ff7d5bf",
        }
    )
    return common
