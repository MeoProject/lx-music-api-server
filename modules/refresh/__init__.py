from utils import scheduler
from server.config import config
from .kg import refreshLogin as kg_refreshLogin
from .tx import refreshLogin as tx_refreshLogin


def reg_refreshLogin_pool_task():
    tx_user_info_pool = config.read("modules.platform.tx.users")
    for tx_user_info in tx_user_info_pool:
        if tx_user_info["refreshLogin"]:
            scheduler.append(
                f"刷新ck_QQ音乐: {tx_user_info['uin']}",
                tx_refreshLogin,
                86400,
                args={"user_info": tx_user_info},
            )

    kg_user_info_pool = config.read("modules.platform.kg.users")
    for user_info in kg_user_info_pool:
        if user_info["refreshLogin"]:
            scheduler.append(
                f"刷新ck_酷狗音乐: {user_info['userid']}",
                kg_refreshLogin,
                86400,
                args={"user_info": user_info},
            )


reg_refreshLogin_pool_task()
