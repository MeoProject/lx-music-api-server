# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: refresh_login.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common import Httpx, variable, scheduler, config, log
from .utils import sign
import ujson as json
from typing import Dict, Any, Optional

logger = log.log("qqmusic_refresh_login")


def _build_request_body(user_info: Dict[str, Any]) -> Dict[str, Any]:
    """构建统一请求体结构"""
    return {
        "comm": {
            "fPersonality": "0",
            "tmeLoginType": "2"
            if user_info["qqmusic_key"].startswith("Q_H_L")
            else "1",
            "qq": str(user_info["uin"]),
            "authst": user_info["qqmusic_key"],
            "ct": "11",
            "cv": "12080008",
            "v": "12080008",
            "tmeAppID": "qqmusic",
        },
        "req1": {
            "module": "music.login.LoginServer",
            "method": "Login",
            "param": {
                "str_musicid": str(user_info["uin"]),
                "musickey": user_info["qqmusic_key"],
                "refresh_key": user_info.get("refresh_key", ""),
            },
        },
    }


async def _update_user_config(
    user_info: Dict[str, Any], new_data: Dict[str, Any]
) -> None:
    """统一更新用户配置"""
    updates = {
        "uin": str(new_data.get("musicid", user_info["uin"])),
        "qqmusic_key": new_data.get("musickey", user_info["qqmusic_key"]),
        "refresh_key": new_data.get("refresh_key", user_info.get("refresh_key", "")),
    }

    if variable.use_cookie_pool:
        user_list = config.read_config("module.cookiepool.tx")
        target_user = next((u for u in user_list if u["uin"] == user_info["uin"]), None)
        if target_user:
            target_user.update(updates)
            config.write_config("module.cookiepool.tx", user_list)
    else:
        for key, value in updates.items():
            config.write_config(f"module.tx.user.{key}", value)


async def _process_refresh(user_info: Dict[str, Any]) -> Optional[bool]:
    """统一处理刷新逻辑"""
    try:
        # 构建请求参数
        request_body = _build_request_body(user_info)
        signature = sign(json.dumps(request_body))

        # 发送请求
        response = await Httpx.AsyncRequest(
            f"https://u.y.qq.com/cgi-bin/musics.fcg?sign={signature}",
            {
                "method": "POST",
                "body": json.dumps(request_body),
                "headers": {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                },
            },
        )

        response_data = response.json()
        if response_data.get("req1", {}).get("code") != 0:
            logger.warning(
                f"刷新失败 [账号: {user_info['uin']} 代码: {response_data['req1']['code']}]"
            )
            return False

        # 更新配置
        await _update_user_config(user_info, response_data["req1"]["data"])
        logger.info(f"刷新成功 [账号: {user_info['uin']}]")
        return True

    except json.JSONDecodeError:
        logger.error(
            "响应解析失败 [账号: %s] 原始响应: %s",
            user_info["uin"],
            response.text[:100],
        )
    except KeyError as e:
        logger.error(
            "响应数据格式异常 [账号: %s] 缺失字段: %s", user_info["uin"], str(e)
        )
    except Exception as e:
        logger.error(
            "刷新过程异常 [账号: %s] 错误信息: %s",
            user_info["uin"],
            str(e),
        )
    return False


async def refresh() -> None:
    """主刷新入口（非Cookie池模式）"""
    if not config.read_config("module.tx.user.refresh_login.enable"):
        return
    await _process_refresh(
        {
            "uin": config.read_config("module.tx.user.uin"),
            "qqmusic_key": config.read_config("module.tx.user.qqmusic_key"),
            "refresh_key": config.read_config("module.tx.user.refresh_key"),
        }
    )


async def refresh_login_for_pool(user_info: Dict[str, Any]) -> None:
    """Cookie池刷新入口"""
    if user_info.get("refresh_login", {}).get("enable", False):
        await _process_refresh(user_info)


def _setup_scheduler() -> None:
    """初始化定时任务"""
    if variable.use_cookie_pool:
        user_list = config.read_config("module.cookiepool.tx")
        for user in user_list:
            if user.get("refresh_login", {}).get("enable", False):
                scheduler.append(
                    f"qq_refresh_{user['uin']}",
                    refresh_login_for_pool,
                    user["refresh_login"].get("interval", 3600),
                    args={"user_info": user},
                )
    elif config.read_config("module.tx.user.refresh_login.enable"):
        scheduler.append(
            "qqmusic_main_refresh",
            refresh,
            config.read_config("module.tx.user.refresh_login.interval"),
        )


# 初始化定时任务
_setup_scheduler()
