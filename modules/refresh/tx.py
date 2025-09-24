from utils import log
from server.config import config
from modules.plat.tx.utils import signRequest
from modules.plat.tx import build_common_params

logger = log.createLogger("Refresh Login")


async def refresh_login(user_info):
    if user_info["uin"] in [0, "", "0"]:
        return
    if user_info["token"] == "":
        return

    params = {
        "req": {
            "module": "music.login.LoginServer",
            "method": "Login",
            "param": {
                "openid": user_info["openId"],
                "access_token": user_info["accessToken"],
                "refresh_token": "",
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

    params["comm"] = await build_common_params(user_info)

    req = await signRequest(params)
    body = req.json()

    if body["req"]["code"] != 0:
        logger.warning(
            f'为QQ音乐账号({user_info["uin"]})刷新登录失败, code: '
            + str(body["req"]["code"])
            + f"\n响应体: {body}"
        )
        return
    else:
        logger.info(f'为QQ音乐账号({user_info["uin"]})刷新登录成功')

        user_list = config.read("module.platform.tx.users")
        user_list[user_list.index(user_info)]["uin"] = str(
            body["req"]["data"]["musicid"]
        )
        user_list[user_list.index(user_info)]["token"] = body["req"]["data"]["musickey"]
        user_list[user_list.index(user_info)]["openId"] = body["req"]["data"]["openid"]
        user_list[user_list.index(user_info)]["accessToken"] = body["req"]["data"][
            "access_token"
        ]
        user_list[user_list.index(user_info)]["refreshKey"] = body["req"]["data"][
            "refresh_key"
        ]

        if body["req_2"]["code"] != 0:
            logger.warning(
                f'为QQ音乐账号({user_info["uin"]})检查VIP状态失败, code: '
                + str(body["req_2"]["code"])
                + f"\n响应体: {body}"
            )
            vip_type = "normal"
        else:
            data = body["req_2"]["data"]["identity"]
            if bool(data["HugeVip"]):
                vip_type = "svip"
                logger.info(
                    f"QQ音乐账号({user_info['uin']})当前是SVIP，过期时间：{data['HugeVipEnd']}"
                )
            elif bool(data["LMFlag"]):
                vip_type = "vip"
                logger.info(
                    f"QQ音乐账号({user_info['uin']})当前是绿钻VIP，过期时间：{data['LMEnd']}"
                )
            elif bool(data["vip"]):
                vip_type = "vip"
                logger.warning(f'QQ音乐账号({user_info["uin"]})可能是绿钻VIP')
            else:
                vip_type = "normal"
                logger.warning(f'QQ音乐账号({user_info["uin"]})不是VIP')

        user_list[user_list.index(user_info)]["vip_type"] = vip_type

        config.write("module.platform.tx.users", user_list)
        logger.info(f'为QQ音乐账号({user_info["uin"]})数据更新完毕')
