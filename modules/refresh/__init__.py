from server.config import config
from utils import scheduler
from .kg import refresh_login as kg_refresh_login
from .tx import refresh_login as tx_refresh_login


def reg_refresh_login_pool_task():
    tx_user_info_pool = config.read("module.platform.tx.users")
    for tx_user_info in tx_user_info_pool:
        if tx_user_info["refresh_login"]:
            scheduler.append(
                f'刷新ck_QQ音乐: {tx_user_info["uin"]}',
                tx_refresh_login,
                86400,
                args={"user_info": tx_user_info},
            )

    user_info_pool = config.read("module.platform.kg.users")
    for user_info in user_info_pool:
        if user_info["refresh_login"]:
            scheduler.append(
                f'刷新ck_酷狗音乐: {user_info["userid"]}',
                kg_refresh_login,
                86400,
                args={"user_info": user_info},
            )


reg_refresh_login_pool_task()
