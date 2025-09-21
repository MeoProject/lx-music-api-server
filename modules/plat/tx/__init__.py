from . import sign
from . import utils

from typing import Any
from utils import device, qimei

COMMON_DEFAULTS: dict[str, str] = {
    "ct": "11",
    "cv": "14080008",
    "v": "14080008",
    "chid": "2005000982",
    "tmeAppID": "qqmusic",
    "format": "json",
    "inCharset": "utf-8",
    "outCharset": "utf-8",
}

DEVICE = device.get_cached_device()


async def build_common_params(
    user_info: dict[str, str | int | None] | None = None,
) -> dict[str, Any]:
    QIMEI = await qimei.get_qimei("11.2.3")

    common = {
        "QIMEI36": QIMEI["q36"],
        "QIMEI": QIMEI["q16"],
    }
    common.update(COMMON_DEFAULTS)
    if user_info != None and user_info.get("uin") and user_info.get("token"):
        common.update(
            {
                "qq": str(user_info["uin"]),
                "authst": user_info["token"],
                "tmeLoginType": "2",
            }
        )
    common.update(
        {
            "os_ver": DEVICE.version.release,
            "phonetype": DEVICE.model,
            "devicelevel": DEVICE.version.sdk,
            "rom": DEVICE.fingerprint,
            "aid": DEVICE.android_id,
            "nettype": DEVICE.apn,
            "udid": "ffffffffbff94f7d000000000033c587",
            "OpenUDID": "ffffffffbff94f7d000000000033c587",
            "OpenUDID2": "ffffffffbff94f7d000001996c7fddff",
            "QIMEI36": "0fd8b521df8415e5d25da4ba100012e19915",
        }
    )
    return common
