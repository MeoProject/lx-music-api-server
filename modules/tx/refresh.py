from common import scheduler
from common import config
from common import log
from .utils import signRequest

logger = log.log("Refresh Login")


async def check_vip(user_info):
    options = {
        "comm": {
            "ct": "26",
            "cv": "2010101",
            "v": "2010101",
            "authst": user_info["token"],
            "qq": int(user_info["uin"]),
        },
        "request": {
            "module": "VipLogin.VipLoginInter",
            "method": "vip_login_base",
            "param": {},
        },
    }

    req = await signRequest(options)
    body = req.json()

    if body["request"]["code"] != 0:
        logger.warning(
            f'为QQ音乐账号({user_info["uin"]})检查VIP状态失败, code: '
            + str(body["request"]["code"])
            + f"\n响应体: {body}"
        )
        return "normal"
    else:
        data = body["request"]["data"]["identity"]
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
        return vip_type


async def refresh_login(user_info):
    if user_info["uin"] in [0, "", "0"]:
        return
    if user_info["token"] == "":
        return

    requestParams = {
        "comm": {
            "ct": "11",
            "cv": "12050505",
            "v": "12050505",
            "chid": "2005000894",
            "tmeLoginMethod": "2",
            "tmeLoginType": "2",
            "OpenUDID2": user_info["devices"]["UDID2"],
            "QIMEI36": user_info["devices"]["QIMEI"],
            "tmeAppID": "qqmusic",
            "rom": user_info["devices"]["fingerprint"],
            "fPersonality": "0",
            "OpenUDID": user_info["devices"]["UDID"],
            "udid": user_info["devices"]["UDID"],
            "os_ver": user_info["devices"]["osver"],
            "aid": user_info["devices"]["aid"],
            "phonetype": user_info["devices"]["model"],
            "devicelevel": user_info["devices"]["level"],
            "newdevicelevel": user_info["devices"]["level"],
            "qq": user_info["uin"],
            "authst": user_info["token"],
        },
        "req": {
            "module": "music.login.LoginServer",
            "method": "Login",
            "param": {
                "openid": user_info["openId"],
                "access_token": user_info["accessToken"],
                "refresh_token": user_info["refreshToken"],
                "musicid": int(user_info["uin"]),
                "musickey": user_info["token"],
                "refresh_key": user_info["refreshKey"],
                "loginMode": 2,
            },
        },
    }
    req = await signRequest(requestParams)
    body = req.json()
    if body["req"]["code"] != 0:
        logger.warning(
            f'为QQ音乐账号({user_info["uin"]})刷新登录失败, code: '
            + str(body["req"]["code"])
            + f"\n响应体: {body}"
        )
        return
    else:
        logger.info(f'为QQ音乐账号(_{user_info["uin"]})刷新登录成功')
        user_list = config.ReadConfig("module.tx.users")
        user_list[user_list.index(user_info)]["token"] = body["req"]["data"]["musickey"]
        user_list[user_list.index(user_info)]["uin"] = str(
            body["req"]["data"]["musicid"]
        )
        user_list[user_list.index(user_info)]["openId"] = str(
            body["req"]["data"]["openid"]
        )
        user_list[user_list.index(user_info)]["accessToken"] = str(
            body["req"]["data"]["access_token"]
        )
        user_list[user_list.index(user_info)]["vip_type"] = await check_vip(user_info)
        config.WriteConfig("module.tx.users", user_list)
        logger.info(f'为QQ音乐账号({user_info["uin"]})数据更新完毕')
        return


def reg_refresh_login_pool_task():
    user_info_pool = config.ReadConfig("module.tx.users")
    for user_info in user_info_pool:
        if user_info["refresh_login"]:
            scheduler.append(
                f'Q音ck刷新：{user_info["uin"]}',
                refresh_login,
                43000,
                args={"user_info": user_info},
            )


reg_refresh_login_pool_task()
