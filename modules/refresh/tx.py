from utils import log
from server.config import config
from modules.plat.tx.utils import signRequest
from modules.plat.tx import build_comm

logger = log.createLogger("Refresh Login")


async def refreshLogin(user_info):
    if user_info["uin"] in [0, "", "0"]:
        return
    if user_info["token"] == "":
        return

    comm = await build_comm(user_info)
    params = {
        "comm": comm,
        "req": {
            "module": "music.login.LoginServer",
            "method": "Login",
            "param": {
                "openid": user_info["openId"],
                "access_token": user_info["accessToken"],
                "refresh_token": user_info["refreshToken"],
                "expired_in": 0,
                "musicid": int(user_info["uin"]),
                "musickey": user_info["token"],
                "refresh_key": user_info["refreshKey"],
                "loginMode": 2,
            },
        },
        "req_2": {
            "module": "VipLogin.VipLoginInter",
            "method": "vip_login_base",
            "param": {},
        },
    }

    req = await signRequest(params)
    body = req.json()

    if body["req"]["code"] != 0:
        logger.warning(
            f"为QQ音乐官方账号({user_info['uin']})刷新登录失败, code: "
            + str(body["req"]["code"])
            + f"\n响应体: {body}"
        )
        return
    else:
        logger.info(f"为QQ音乐官方账号({user_info['uin']})刷新登录成功")

        user_list = config.read("modules.platform.tx.users")

        user_index = None
        for i, user in enumerate(user_list):
            if str(user.get("uin")) == str(user_info["uin"]):
                user_index = i
                break

        user_list[user_index]["token"] = body["req"]["data"]["musickey"]
        user_list[user_index]["uin"] = str(body["req"]["data"]["musicid"])
        user_list[user_index]["openId"] = str(body["req"]["data"]["openid"])
        user_list[user_index]["accessToken"] = str(body["req"]["data"]["access_token"])
        user_list[user_index]["refreshKey"] = str(body["req"]["data"]["refresh_key"])

        if body["req_2"]["code"] != 0:
            logger.warning(
                f"为QQ音乐官方账号({user_info['uin']})检查VIP状态失败, code: "
                + str(body["req_2"]["code"])
                + f"\n响应体: {body}"
            )
            vipType = "normal"
        else:
            data = body["req_2"]["data"]["identity"]
            if bool(data["HugeVip"]):
                vipType = "svip"
                logger.info(
                    f"QQ音乐官方账号({user_info['uin']})当前是SVIP，过期时间：{data['HugeVipEnd']}"
                )
            elif bool(data["LMFlag"]):
                vipType = "vip"
                logger.info(
                    f"QQ音乐官方账号({user_info['uin']})当前是绿钻VIP，过期时间：{data['LMEnd']}"
                )
            elif bool(data["vip"]):
                vipType = "vip"
                logger.warning(f"QQ音乐官方账号({user_info['uin']})可能是绿钻VIP")
            else:
                vipType = "normal"
                logger.warning(f"QQ音乐官方账号({user_info['uin']})不是VIP")

        user_list[user_index]["vipType"] = vipType

        config.write("modules.platform.tx.users", user_list)
        logger.info(f"为QQ音乐官方账号({user_info['uin']})数据更新完毕")
