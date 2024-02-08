import flet
import ujson as json
import os
import ast


# from ChatGPT
def update_nested_json(json_obj, updates):
    for key, value in updates.items():
        if key in json_obj:
            if isinstance(value, dict) and isinstance(json_obj[key], dict):
                update_nested_json(json_obj[key], value)
            elif isinstance(value, list) and isinstance(json_obj[key], list):
                if len(value) == len(json_obj[key]):
                    for i in range(len(value)):
                        if isinstance(value[i], dict) and isinstance(
                            json_obj[key][i], dict
                        ):
                            update_nested_json(json_obj[key][i], value[i])
                        else:
                            json_obj[key][i] = value[i]
                else:
                    json_obj[key] = value
            else:
                json_obj[key] = value
        else:
            json_obj[key] = value
    return json_obj


def toint(page: flet.Page, arg):
    # def closeFailedDialog(e):
    #     failedDialog.open = False
    #     page.update()
    # failedDialog = flet.AlertDialog(
    #     modal=True,
    #     title=flet.Text('Update failed', color='FF0000'),
    #     content=flet.Text('Please Check You Input\n\n'+str(arg)),
    #     actions=[flet.TextButton("OK", on_click=closeFailedDialog)],
    #     actions_alignment=flet.MainAxisAlignment.END,
    # )
    # def openFailedDialog():
    #     page.dialog = failedDialog
    #     failedDialog.open = True
    #     page.update()

    try:
        return int(arg)
    except:
        # openFailedDialog()
        return None


def _Save(page: flet.Page, args):
    def closeSuccessDialog(e):
        successDialog.open = False
        page.update()

    successDialog = flet.AlertDialog(
        modal=True,
        title=flet.Text("Update success"),
        content=flet.Text(
            "Update Content: "
            + str(args)
            + "\n\nYour original config.json file have been rename configN.bak"
        ),
        actions=[flet.TextButton("OK", on_click=closeSuccessDialog)],
        actions_alignment=flet.MainAxisAlignment.END,
    )

    def openSuccessDialog():
        page.dialog = successDialog
        successDialog.open = True
        page.update()

    def closeFailedDialog(e):
        failedDialog.open = False
        page.update()

    failedDialog = flet.AlertDialog(
        modal=True,
        title=flet.Text("Update failed", color="FF0000"),
        content=flet.Text("Please Check You Input\n\n" + str(args)),
        actions=[flet.TextButton("OK", on_click=closeFailedDialog)],
        actions_alignment=flet.MainAxisAlignment.END,
    )

    def openFailedDialog():
        page.dialog = failedDialog
        failedDialog.open = True
        page.update()

    # print(args)

    try:
        with open("config.json", "r+", encoding="utf-8") as f:
            config = json.loads(f.read())
        config = update_nested_json(config, args)

        i = 1
        while 1:
            try:
                os.rename("config.json", f"config{i}.bak")
                break
            except:
                i += 1

        with open("config.json", "w+", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    config, indent=4, ensure_ascii=False, escape_forward_slashes=False
                )
            )
        openSuccessDialog()
    except:
        openFailedDialog()


def _404(page: flet.Page):
    return [
        flet.Container(
            content=flet.Text(value="404", size=50), alignment=flet.alignment.center
        ),
        flet.Container(
            content=flet.ElevatedButton("返回主页", on_click=lambda _: page.go("/")),
            alignment=flet.alignment.center,
        ),
    ]


# def _Save_Cookiepool(page: flet.Page, p, v):
#     return []


def CommonPage(page: flet.Page):
    common = config["common"]
    common_host_label = flet.TextField(
        label="服务器启动时所使用的HOST地址", value=common["host"]
    )
    common_ports_label = flet.TextField(
        label="服务器启动时所使用的端口,使用list格式", value=common["ports"]
    )
    common_ssl_info_label = flet.ElevatedButton(
        "服务器https配置", on_click=lambda _: page.go("/common/ssl_info")
    )
    common_reverse_proxy_label = flet.ElevatedButton(
        "针对类似于nginx一类的反代的配置",
        on_click=lambda _: page.go("/common/reverse_proxy"),
    )
    common_debug_mode_label = flet.Checkbox(
        label="是否开启调试模式", value=common["debug_mode"]
    )
    common_log_length_limit_label = flet.TextField(
        label="单条日志长度限制", value=common["log_length_limit"]
    )
    common_fakeip_label = flet.TextField(
        label="服务器在海外时的IP伪装值", value=common["fakeip"]
    )
    common_proxy_label = flet.ElevatedButton(
        "代理配置，HTTP与HTTPS协议需分开配置",
        on_click=lambda _: page.go("/common/proxy"),
    )
    common_log_file_label = flet.Checkbox(
        label="是否开启日志文件", value=bool(common["log_file"])
    )
    common_cookiepool_label = flet.Checkbox(
        label="是否开启cookie池", value=bool(config["common"]["cookiepool"])
    )
    common_download_config_label = flet.ElevatedButton(
        "下载脚本配置", on_click=lambda _: page.go("/common/download_config")
    )

    return [
        common_host_label,
        common_ports_label,
        common_ssl_info_label,
        common_reverse_proxy_label,
        common_debug_mode_label,
        common_log_length_limit_label,
        common_fakeip_label,
        common_proxy_label,
        common_log_file_label,
        common_cookiepool_label,
        flet.Text("这将允许用户配置多个cookie并在请求时随机使用一个"),
        flet.Text(
            "启用后请在module.cookiepool中配置cookie，在user处配置的cookie会被忽略"
        ),
        flet.Text("cookiepool中格式统一为列表嵌套user处的cookie的字典"),
        common_download_config_label,
        flet.ElevatedButton("返回", on_click=lambda _: page.go("/")),
        flet.ElevatedButton(
            "保存",
            on_click=lambda _: _Save(
                page,
                {
                    "common": {
                        "host": str(common_host_label.value),
                        "ports": json.loads(
                            str(common_ports_label.value).replace("'", '"')
                        ),
                        "debug_mode": bool(common_debug_mode_label.value),
                        "log_length_limit": toint(
                            page, common_log_length_limit_label.value
                        ),
                        "fakeip": str(common_fakeip_label.value),
                        "log_file": bool(common_log_file_label.value),
                        "cookiepool": bool(common_cookiepool_label.value),
                    }
                },
            ),
        ),
    ]


def CommonPageExpand(page: flet.Page):
    if page.route.split("/")[2] == "ssl_info":
        ssl_info = config["common"]["ssl_info"]
        common_is_https_label = flet.Checkbox(
            label="是否开启HTTPS", value=bool(ssl_info["is_https"])
        )
        common_enable_label = flet.Checkbox(
            label="启用", value=bool(ssl_info["enable"])
        )
        common_ssl_ports_label = flet.TextField(
            label="SSL端口,使用list格式", value=ssl_info["ssl_ports"]
        )
        common_path_cert_label = flet.TextField(
            label="ssl证书的cert文件地址", value=ssl_info["path"]["cert"]
        )
        common_path_privkey_label = flet.TextField(
            label="ssl证书的private key文件地址", value=ssl_info["path"]["privkey"]
        )
        return [
            flet.Container(
                content=flet.Text(value="SSL Info", size=30),
                alignment=flet.alignment.center,
            ),
            flet.Text(
                '服务器https配置，"是否开启HTTPS"是这个服务器是否是https服务器，如果你使用了反向代理来转发这个服务器，如果它使用了https，也请将它设置为true'
            ),
            common_is_https_label,
            common_enable_label,
            common_ssl_ports_label,
            common_path_cert_label,
            common_path_privkey_label,
            flet.ElevatedButton("返回", on_click=lambda _: page.go("/common")),
            flet.ElevatedButton(
                "保存",
                on_click=lambda _: _Save(
                    page,
                    {
                        "common": {
                            "ssl_info": {
                                "is_https": bool(common_is_https_label.value),
                                "enable": bool(common_enable_label.value),
                                "ssl_ports": json.loads(
                                    str(common_ssl_ports_label.value).replace("'", '"')
                                ),
                                "path": {
                                    "cert": str(common_path_cert_label.value),
                                    "privkey": str(common_path_privkey_label.value),
                                },
                            }
                        }
                    },
                ),
            ),
        ]
    elif page.route.split("/")[2] == "reverse_proxy":
        reverse_proxy = config["common"]["reverse_proxy"]
        common_allow_proxy_label = flet.Checkbox(
            label="是否允许反代", value=bool(reverse_proxy["allow_proxy"])
        )
        common_proxy_whitelist_remote_label = flet.TextField(
            label="反代时允许的ip来源列表，通常为127.0.0.1",
            value=reverse_proxy["proxy_whitelist_remote"],
        )
        common_real_ip_header_label = flet.TextField(
            label="反代来源ip的来源头，不懂请保持默认",
            value=reverse_proxy["real_ip_header"],
        )
        return [
            flet.Container(
                content=flet.Text(value="Reverse Proxy", size=30),
                alignment=flet.alignment.center,
            ),
            common_allow_proxy_label,
            common_proxy_whitelist_remote_label,
            common_real_ip_header_label,
            flet.ElevatedButton("返回", on_click=lambda _: page.go("/common")),
            flet.ElevatedButton(
                "保存",
                on_click=lambda _: _Save(
                    page,
                    {
                        "common": {
                            "reverse_proxy": {
                                "allow_proxy": bool(common_allow_proxy_label.value),
                                "proxy_whitelist_remote": json.loads(
                                    str(
                                        common_proxy_whitelist_remote_label.value
                                    ).replace("'", '"')
                                ),
                                "real_ip_header": str(
                                    common_real_ip_header_label.value
                                ),
                            }
                        }
                    },
                ),
            ),
        ]
    elif page.route.split("/")[2] == "proxy":
        proxy = config["common"]["proxy"]
        common_proxy_enable_label = flet.Checkbox(
            label="是否开启代理", value=bool(proxy["enable"])
        )
        common_http_value_label = flet.TextField(
            label="HTTP协议配置", value=proxy["http_value"]
        )
        common_https_value_label = flet.TextField(
            label="HTTPS协议配置", value=proxy["https_value"]
        )
        return [
            flet.Container(
                content=flet.Text(value="Proxy", size=30),
                alignment=flet.alignment.center,
            ),
            # flet.AppBar(title=flet.Text('proxy'), bgcolor=flet.colors.SURFACE_VARIANT),
            common_proxy_enable_label,
            common_http_value_label,
            common_https_value_label,
            flet.ElevatedButton("返回", on_click=lambda _: page.go("/common")),
            flet.ElevatedButton(
                "保存",
                on_click=lambda _: _Save(
                    page,
                    {
                        "common": {
                            "proxy": {
                                "enable": bool(common_proxy_enable_label.value),
                                "http_value": str(common_http_value_label.value),
                                "https_value": str(common_https_value_label.value),
                            }
                        }
                    },
                ),
            ),
        ]
    elif page.route.split("/")[2] == "download_config":
        download_config = config["common"]["download_config"]
        common_allow_download_script_label = flet.Checkbox(
            label="是否允许直接从服务端下载脚本，开启后可以直接访问 /script?key=你的请求key 下载脚本",
            value=bool(config["common"]["allow_download_script"]),
        )
        common_name_label = flet.TextField(
            label="修改为你的源脚本名称", value=download_config["name"]
        )
        common_intro_label = flet.TextField(
            label="修改为你的源脚本描述", value=download_config["intro"]
        )
        common_author_label = flet.TextField(
            label="修改为你的源脚本作者", value=download_config["author"]
        )
        common_version_label = flet.TextField(
            label="修改为你的源版本", value=download_config["version"]
        )
        common_filename_label = flet.TextField(
            label="客户端保存脚本时的文件名（可能因浏览器不同出现不一样的情况）",
            value=download_config["filename"],
        )
        common_dev_label = flet.Checkbox(
            label="是否启用开发模式", value=bool(download_config["dev"])
        )

        # common_quality_label = flet.Tabs(
        #     selected_index=0,
        #     animation_duration=300,
        #     tabs=[
        #         flet.Tab(
        #             text='kw',
        #             content=flet.Row(
        #                 [
        #                     flet.Checkbox(label="128k", value=True),
        #                     flet.Checkbox(label="320k", value=False),
        #                     flet.Checkbox(label="flac", value=False),
        #                     flet.Checkbox(label="flac24bit", value=False),
        #                 ]
        #             ),
        #         ),
        #         flet.Tab(
        #             text='kg',
        #             content=flet.Row(
        #                 [
        #                     flet.Checkbox(label="128k", value=True),
        #                     flet.Checkbox(label="320k", value=False),
        #                     flet.Checkbox(label="flac", value=False),
        #                     flet.Checkbox(label="flac24bit", value=False),
        #                 ]
        #             ),
        #         ),
        #         flet.Tab(
        #             text='tx',
        #             content=flet.Row(
        #                 [
        #                     flet.Checkbox(label="128k", value=True),
        #                     flet.Checkbox(label="320k", value=False),
        #                     flet.Checkbox(label="flac", value=False),
        #                     flet.Checkbox(label="flac24bit", value=False),
        #                 ]
        #             ),
        #         ),
        #         flet.Tab(
        #             text='wy',
        #             content=flet.Row(
        #                 [
        #                     flet.Checkbox(label="128k", value=True),
        #                     flet.Checkbox(label="320k", value=False),
        #                     flet.Checkbox(label="flac", value=False),
        #                     flet.Checkbox(label="flac24bit", value=False),
        #                 ]
        #             ),
        #         ),
        #         flet.Tab(
        #             text='mg',
        #             content=flet.Row(
        #                 [
        #                     flet.Checkbox(label="128k", value=True),
        #                     flet.Checkbox(label="320k", value=False),
        #                     flet.Checkbox(label="flac", value=False),
        #                     flet.Checkbox(label="flac24bit", value=False),
        #                 ]
        #             ),
        #         ),
        #     ],
        #     expand=1,
        # )

        common_quality_label = flet.TextField(
            label="支持的音质", value=download_config["quality"]
        )
        return [
            flet.Container(
                content=flet.Text(value="源脚本的相关配置", size=30),
                alignment=flet.alignment.center,
            ),
            # flet.AppBar(title=flet.Text('源脚本的相关配置'), bgcolor=flet.colors.SURFACE_VARIANT),
            common_allow_download_script_label,
            common_name_label,
            common_intro_label,
            common_author_label,
            common_version_label,
            common_filename_label,
            common_dev_label,
            # flet.Text(value='支持的音质'),
            common_quality_label,
            flet.ElevatedButton("返回", on_click=lambda _: page.go("/common")),
            flet.ElevatedButton(
                "保存",
                on_click=lambda _: _Save(
                    page,
                    {
                        "common": {
                            "allow_download_script": bool(
                                common_allow_download_script_label.value
                            ),
                            "download_config": json.loads(
                                str(common_quality_label.value).replace("'", '"')
                            ),
                        }
                    },
                ),
            ),
        ]
    else:
        return _404(page)


def SecurityPage(page: flet.Page):
    security = config["security"]
    security_rate_limit_label = flet.ElevatedButton(
        "请求速率限制", on_click=lambda _: page.go("/security/rate_limit")
    )
    security_key_label = flet.ElevatedButton(
        "请求key", on_click=lambda _: page.go("/security/key")
    )
    security_whitelist_host_label = flet.TextField(
        label="强制白名单HOST", value=security["whitelist_host"]
    )
    security_check_lxm_label = flet.Checkbox(
        label='是否检查lxm请求头（正常的LX Music以"测试接口"的方式请求时都会携带这个请求头）',
        value=bool(security["check_lxm"]),
    )
    security_lxm_ban_label = flet.Checkbox(
        label="lxm请求头不存在或不匹配时是否将用户IP加入黑名单",
        value=bool(security["lxm_ban"]),
    )
    security_allowed_host_label = flet.ElevatedButton(
        "HOST允许列表", on_click=lambda _: page.go("/security/allowed_host")
    )
    security_banlist_label = flet.ElevatedButton(
        "黑名单", on_click=lambda _: page.go("/security/banlist")
    )

    return [
        security_rate_limit_label,
        security_key_label,
        security_whitelist_host_label,
        security_lxm_ban_label,
        security_check_lxm_label,
        security_allowed_host_label,
        security_banlist_label,
        flet.ElevatedButton("返回", on_click=lambda _: page.go("/")),
        flet.ElevatedButton(
            "保存",
            on_click=lambda _: _Save(
                page,
                {
                    "security": {
                        "whitelist_host": json.loads(
                            str(security_whitelist_host_label.value).replace("'", '"')
                        ),
                        "check_lxm": bool(security_check_lxm_label.value),
                        "lxm_ban": bool(security_lxm_ban_label.value),
                    }
                },
            ),
        ),
    ]


def SecurityPageExpand(page: flet.Page):
    if page.route.split("/")[2] == "rate_limit":
        rate_limit = config["security"]["rate_limit"]
        security_global_label = flet.TextField(
            label="全局请求速率限制", value=rate_limit["global"]
        )
        security_ip_label = flet.TextField(
            label="单个ip请求速率限制", value=rate_limit["ip"]
        )
        return [
            flet.Container(
                content=flet.Text(value="Rate Limit", size=30),
                alignment=flet.alignment.center,
            ),
            # flet.AppBar(title=flet.Text('ssl_info'), bgcolor=flet.colors.SURFACE_VARIANT),
            flet.Text(
                "请求速率限制，填入的值为至少间隔多久才能进行一次请求，单位：秒，不限制请填为0"
            ),
            security_global_label,
            security_ip_label,
            flet.ElevatedButton("返回", on_click=lambda _: page.go("/security")),
            flet.ElevatedButton(
                "保存",
                on_click=lambda _: _Save(
                    page,
                    {
                        "security": {
                            "rate_limit": {
                                "global": toint(page, security_global_label.value),
                                "ip": toint(page, security_ip_label.value),
                            }
                        }
                    },
                ),
            ),
        ]
    elif page.route.split("/")[2] == "key":
        key = config["security"]["key"]
        security_key_enable_label = flet.Checkbox(
            label="是否开启请求key，开启后只有请求头中包含key，且值一样时可以访问API",
            value=bool(key["enable"]),
        )
        security_ban_label = flet.Checkbox(label="ban", value=bool(key["ban"]))
        security_values_label = flet.TextField(
            label="key(使用列表格式)", value=key["values"]
        )

        return [
            flet.Container(
                content=flet.Text(value="Key", size=30), alignment=flet.alignment.center
            ),
            # flet.AppBar(title=flet.Text('ssl_info'), bgcolor=flet.colors.SURFACE_VARIANT),
            security_key_enable_label,
            security_ban_label,
            security_values_label,
            flet.ElevatedButton("返回", on_click=lambda _: page.go("/security")),
            flet.ElevatedButton(
                "保存",
                on_click=lambda _: _Save(
                    page,
                    {
                        "security": {
                            "key": {
                                "enable": bool(security_key_enable_label.value),
                                "ban": bool(security_ban_label.value),
                                "value": json.loads(
                                    str(security_values_label.value).replace("'", '"')
                                ),
                            }
                        }
                    },
                ),
            ),
        ]
    elif page.route.split("/")[2] == "allowed_host":
        allowed_host = config["security"]["allowed_host"]
        security_allowed_host_enable_label = flet.Checkbox(
            label="启用", value=bool(allowed_host["enable"])
        )
        security_list_label = flet.TextField(label="列表", value=allowed_host["list"])
        security_blacklist_enable_label = flet.Checkbox(
            label="启用", value=bool(allowed_host["blacklist"]["enable"])
        )
        security_blacklist_length_label = flet.TextField(
            label="长度", value=allowed_host["blacklist"]["length"]
        )

        return [
            flet.Container(
                content=flet.Text(value="Allowd Host", size=30),
                alignment=flet.alignment.center,
            ),
            # flet.AppBar(title=flet.Text('ssl_info'), bgcolor=flet.colors.SURFACE_VARIANT),
            flet.Text(
                "HOST允许列表，启用后只允许列表内的HOST访问服务器，不需要加端口号"
            ),
            security_allowed_host_enable_label,
            security_list_label,
            flet.Text(
                "当用户访问的HOST并不在允许列表中时是否将请求IP加入黑名单，长度单位：秒"
            ),
            security_blacklist_enable_label,
            security_blacklist_length_label,
            flet.ElevatedButton("返回", on_click=lambda _: page.go("/security")),
            flet.ElevatedButton(
                "保存",
                on_click=lambda _: _Save(
                    page,
                    {
                        "security": {
                            "allowed_host": {
                                "enable": bool(
                                    security_allowed_host_enable_label.value
                                ),
                                "blacklist": {
                                    "enable": bool(
                                        security_blacklist_enable_label.value
                                    ),
                                    "length": toint(
                                        page, security_blacklist_length_label.value
                                    ),
                                },
                                "list": json.loads(
                                    str(security_list_label.value).replace("'", '"')
                                ),
                            }
                        }
                    },
                ),
            ),
        ]
    elif page.route.split("/")[2] == "banlist":
        banlist = config["security"]["banlist"]
        security_banlist_enable_label = flet.Checkbox(
            label="启用", value=bool(banlist["enable"])
        )
        security_expire_enable_label = flet.Checkbox(
            label="启用", value=bool(banlist["expire"]["enable"])
        )
        security_expire_length_label = flet.TextField(
            label="长度", value=banlist["expire"]["length"]
        )

        return [
            flet.Container(
                content=flet.Text(value="Ban List", size=30),
                alignment=flet.alignment.center,
            ),
            # flet.AppBar(title=flet.Text('ssl_info'), bgcolor=flet.colors.SURFACE_VARIANT),
            flet.Text(
                "是否启用黑名单（全局设置，关闭后已存储的值并不受影响，但不会再检查"
            ),
            security_banlist_enable_label,
            flet.Text("是否启用黑名单IP过期（关闭后其他地方的配置会失效）"),
            security_expire_enable_label,
            security_expire_length_label,
            flet.ElevatedButton("返回", on_click=lambda _: page.go("/security")),
            flet.ElevatedButton(
                "保存",
                on_click=lambda _: _Save(
                    page,
                    {
                        "security": {
                            "banlist": {
                                "enable": bool(security_banlist_enable_label.value),
                                "expire": {
                                    "enable": bool(security_expire_enable_label),
                                    "length": toint(
                                        page, security_expire_length_label.value
                                    ),
                                },
                            }
                        }
                    },
                ),
            ),
        ]
    return [flet.ElevatedButton("返回", on_click=lambda _: page.go("/security"))]


def ModulePage(page: flet.Page):
    kg_label = flet.ElevatedButton("kg", on_click=lambda _: page.go("/module/kg"))
    tx_label = flet.ElevatedButton("tx", on_click=lambda _: page.go("/module/tx"))
    wy_label = flet.ElevatedButton("wy", on_click=lambda _: page.go("/module/wy"))
    mg_label = flet.ElevatedButton("mg", on_click=lambda _: page.go("/module/mg"))
    kw_label = flet.ElevatedButton("kw", on_click=lambda _: page.go("/module/kw"))
    cookiepool_label = flet.ElevatedButton(
        "cookiepool", on_click=lambda _: page.go("/module/cookiepool")
    )

    return [
        kg_label,
        tx_label,
        wy_label,
        mg_label,
        kw_label,
        cookiepool_label,
        flet.ElevatedButton("返回", on_click=lambda _: page.go("/")),
    ]


def ModulePageExpand(page: flet.Page):
    if page.route.split("/")[2] == "kg":
        if page.route.split("/")[-1] == "kg":
            return [
                flet.Container(
                    content=flet.Text(value="酷狗音乐相关配置", size=30),
                    alignment=flet.alignment.center,
                ),
                flet.ElevatedButton(
                    "client", on_click=lambda _: page.go("/module/kg/client")
                ),
                flet.ElevatedButton(
                    "tracker", on_click=lambda _: page.go("/module/kg/tracker")
                ),
                flet.ElevatedButton(
                    "user", on_click=lambda _: page.go("/module/kg/user")
                ),
                flet.ElevatedButton("返回", on_click=lambda _: page.go("/module")),
            ]
        else:
            if page.route.split("/")[3] == "client":
                kg_client = config["module"]["kg"]["client"]
                module_kg_client_appid_label = flet.TextField(
                    label="酷狗音乐的appid，官方安卓为1005，官方PC为1001",
                    value=kg_client["appid"],
                )
                module_kg_client_signatureKey_label = flet.TextField(
                    label="客户端signature采用的key值，需要与appid对应",
                    value=kg_client["signatureKey"],
                )
                module_kg_client_clientver_label = flet.TextField(
                    label="客户端versioncode，pidversionsecret可能随此值而变化",
                    value=kg_client["clientver"],
                )
                module_kg_client_pidversionsecret_label = flet.TextField(
                    label="获取URL时所用的key值计算验证值",
                    value=kg_client["pidversionsecret"],
                )
                module_kg_client_pid_label = flet.TextField(
                    label="pid", value=kg_client["pid"]
                )

                return [
                    flet.Container(
                        content=flet.Text(
                            value="客户端请求配置，不懂请保持默认", size=30
                        ),
                        alignment=flet.alignment.center,
                    ),
                    module_kg_client_appid_label,
                    module_kg_client_signatureKey_label,
                    module_kg_client_clientver_label,
                    module_kg_client_pidversionsecret_label,
                    module_kg_client_pid_label,
                    flet.ElevatedButton(
                        "返回", on_click=lambda _: page.go("/module/kg")
                    ),
                    flet.ElevatedButton(
                        "保存",
                        on_click=lambda _: _Save(
                            page,
                            {
                                "module": {
                                    "kg": {
                                        "client": {
                                            "appid": str(
                                                module_kg_client_appid_label.value
                                            ),
                                            "signatureKey": str(
                                                module_kg_client_signatureKey_label.value
                                            ),
                                            "clientver": str(
                                                module_kg_client_clientver_label.value
                                            ),
                                            "pidversionsecret": str(
                                                module_kg_client_pidversionsecret_label.value
                                            ),
                                            "pid": str(
                                                module_kg_client_pid_label.value
                                            ),
                                        }
                                    }
                                }
                            },
                        ),
                    ),
                ]
            elif page.route.split("/")[3] == "tracker":
                kg_tracker = config["module"]["kg"]["tracker"]
                module_kg_tracker_host_label = flet.TextField(
                    label="host", value=kg_tracker["host"]
                )
                module_kg_tracker_path_label = flet.TextField(
                    label="path", value=kg_tracker["path"]
                )
                module_kg_tracker_version_label = flet.TextField(
                    label="客户端versioncode，pidversionsecret可能随此值而变化",
                    value=kg_tracker["version"],
                )
                module_kg_tracker_xrouter_enable_label = flet.Checkbox(
                    label="启用", value=bool(kg_tracker["x-router"]["enable"])
                )
                module_kg_tracker_xrouter_value_label = flet.TextField(
                    label="x-router", value=kg_tracker["x-router"]["value"]
                )
                module_kg_tracker_extra_params_label = flet.TextField(
                    label="自定义添加的param，优先级大于默认，填写类型为普通的JSON数据，会自动转换为请求param",
                    value=kg_tracker["extra_params"],
                )

                return [
                    flet.Container(
                        content=flet.Text(
                            value="trackerapi请求配置，不懂请保持默认", size=30
                        ),
                        alignment=flet.alignment.center,
                    ),
                    module_kg_tracker_host_label,
                    module_kg_tracker_path_label,
                    module_kg_tracker_version_label,
                    flet.Text(
                        "当host为gateway.kugou.com时需要追加此头，为tracker类地址时则不需要"
                    ),
                    module_kg_tracker_xrouter_enable_label,
                    module_kg_tracker_xrouter_value_label,
                    module_kg_tracker_extra_params_label,
                    flet.ElevatedButton(
                        "返回", on_click=lambda _: page.go("/module/kg")
                    ),
                    flet.ElevatedButton(
                        "保存",
                        on_click=lambda _: _Save(
                            page,
                            {
                                "module": {
                                    "kg": {
                                        "tracker": {
                                            "host": str(
                                                module_kg_tracker_host_label.value
                                            ),
                                            "path": str(
                                                module_kg_tracker_path_label.value
                                            ),
                                            "version": str(
                                                module_kg_tracker_version_label.value
                                            ),
                                            "x-router": {
                                                "enable": bool(
                                                    module_kg_tracker_xrouter_enable_label.value
                                                ),
                                                "value": str(
                                                    module_kg_tracker_xrouter_value_label.value
                                                ),
                                            },
                                            "extra_params": json.loads(
                                                str(
                                                    module_kg_tracker_extra_params_label.value
                                                ).replace("'", '"')
                                            ),
                                        }
                                    }
                                }
                            },
                        ),
                    ),
                ]
            elif page.route.split("/")[3] == "user":
                kg_user = config["module"]["kg"]["user"]
                module_kg_user_token_label = flet.TextField(
                    label="token", value=kg_user["token"]
                )
                module_kg_user_userid_label = flet.TextField(
                    label="userid", value=kg_user["userid"]
                )
                module_kg_user_mid_label = flet.TextField(
                    label="mid", value=kg_user["mid"]
                )
                module_kg_user_lite_sign_in_enable_label = flet.Checkbox(
                    label="启用", value=bool(kg_user["lite_sign_in"]["enable"])
                )
                module_kg_user_lite_sign_in_interval_label = flet.TextField(
                    label="interval", value=kg_user["lite_sign_in"]["interval"]
                )
                module_kg_user_lite_sign_in_mixsongmid_label = flet.TextField(
                    label="mix_songmid的获取方式, 默认auto, 可以改成一个数字手动",
                    value=kg_user["lite_sign_in"]["mixsongmid"]["value"],
                )

                return [
                    flet.Container(
                        content=flet.Text(
                            value="此处内容请统一抓包获取，需要vip账号来获取会员歌曲，如果没有请留为空值，mid必填，可以瞎填一段数字",
                            size=30,
                        ),
                        alignment=flet.alignment.center,
                    ),
                    module_kg_user_token_label,
                    module_kg_user_userid_label,
                    module_kg_user_mid_label,
                    flet.Text("是否启用概念版自动签到，仅在appid=3116时运行"),
                    module_kg_user_lite_sign_in_enable_label,
                    module_kg_user_lite_sign_in_interval_label,
                    module_kg_user_lite_sign_in_mixsongmid_label,
                    flet.ElevatedButton(
                        "返回", on_click=lambda _: page.go("/module/kg")
                    ),
                    flet.ElevatedButton(
                        "保存",
                        on_click=lambda _: _Save(
                            page,
                            {
                                "module": {
                                    "kg": {
                                        "user": {
                                            "token": str(
                                                module_kg_user_token_label.value
                                            ),
                                            "userid": str(
                                                module_kg_user_userid_label.value
                                            ),
                                            "mid": str(module_kg_user_mid_label.value),
                                            "lite_sign_in": {
                                                "enable": bool(
                                                    module_kg_user_lite_sign_in_enable_label.value
                                                ),
                                                "interval": toint(
                                                    page,
                                                    module_kg_user_lite_sign_in_interval_label.value,
                                                ),
                                                "mixsongmid": {
                                                    "value": str(
                                                        module_kg_user_lite_sign_in_mixsongmid_label.value
                                                    )
                                                },
                                            },
                                        }
                                    }
                                }
                            },
                        ),
                    ),
                ]
            else:
                return _404(page)

    elif page.route.split("/")[2] == "tx":
        if page.route.split("/")[-1] == "tx":
            module_tx_cdnaddr_label = flet.TextField(
                label="CDN地址", value=config["module"]["tx"]["cdnaddr"]
            )
            return [
                flet.Container(
                    content=flet.Text(value="QQ音乐相关配置", size=30),
                    alignment=flet.alignment.center,
                ),
                flet.ElevatedButton(
                    "vkeyserver", on_click=lambda _: page.go("/module/tx/vkeyserver")
                ),
                flet.ElevatedButton(
                    "user", on_click=lambda _: page.go("/module/tx/user")
                ),
                module_tx_cdnaddr_label,
                flet.ElevatedButton("返回", on_click=lambda _: page.go("/module")),
                flet.ElevatedButton(
                    "保存",
                    on_click=lambda _: _Save(
                        page,
                        {
                            "module": {
                                "tx": {"cdnaddr": str(module_tx_cdnaddr_label.value)}
                            }
                        },
                    ),
                ),
            ]
        else:
            if page.route.split("/")[3] == "vkeyserver":
                tx_vkeyserver = config["module"]["tx"]["vkeyserver"]
                module_tx_vkeyserver_guid_label = flet.TextField(
                    label="guid", value=tx_vkeyserver["guid"]
                )
                module_tx_vkeyserver_uin_label = flet.TextField(
                    label="uin", value=tx_vkeyserver["uin"]
                )
                return [
                    flet.Container(
                        content=flet.Text(
                            value="请求官方api时使用的guid，uin等信息，不需要与cookie中信息一致",
                            size=30,
                        ),
                        alignment=flet.alignment.center,
                    ),
                    module_tx_vkeyserver_guid_label,
                    module_tx_vkeyserver_uin_label,
                    flet.ElevatedButton(
                        "返回", on_click=lambda _: page.go("/module/tx")
                    ),
                    flet.ElevatedButton(
                        "保存",
                        on_click=lambda _: _Save(
                            page,
                            {
                                "module": {
                                    "tx": {
                                        "vkeyserver": {
                                            "guid": str(
                                                module_tx_vkeyserver_guid_label.value
                                            ),
                                            "uin": str(
                                                module_tx_vkeyserver_uin_label.value
                                            ),
                                        }
                                    }
                                }
                            },
                        ),
                    ),
                ]
            elif page.route.split("/")[3] == "user":
                tx_user = config["module"]["tx"]["user"]
                module_tx_user_qqmusic_key_label = flet.TextField(
                    label="qqmusic_key    可以从Cookie中/客户端的请求体中（comm.authst）获取",
                    value=tx_user["qqmusic_key"],
                )
                module_tx_user_uin_label = flet.TextField(
                    label="key对应的QQ号", value=tx_user["uin"]
                )
                module_tx_user_refresh_login_enable_label = flet.Checkbox(
                    label="启用", value=bool(tx_user["refresh_login"]["enable"])
                )
                module_tx_user_refresh_login_interval_label = flet.TextField(
                    label="interval刷新间隔", value=tx_user["refresh_login"]["interval"]
                )

                return [
                    flet.Container(
                        content=flet.Text(
                            value="用户数据，可以通过浏览器获取，需要vip账号来获取会员歌曲，如果没有请留为空值",
                            size=30,
                        ),
                        alignment=flet.alignment.center,
                    ),
                    module_tx_user_qqmusic_key_label,
                    module_tx_user_uin_label,
                    flet.Text("刷新登录相关配置"),
                    module_tx_user_refresh_login_enable_label,
                    module_tx_user_refresh_login_interval_label,
                    flet.ElevatedButton(
                        "返回", on_click=lambda _: page.go("/module/tx")
                    ),
                    flet.ElevatedButton(
                        "保存",
                        on_click=lambda _: _Save(
                            page,
                            {
                                "module": {
                                    "tx": {
                                        "user": {
                                            "qqmusic_key": str(
                                                module_tx_user_qqmusic_key_label.value
                                            ),
                                            "uin": str(module_tx_user_uin_label.value),
                                            "refresh_login": {
                                                "enable": bool(
                                                    module_tx_user_refresh_login_enable_label.value
                                                ),
                                                "interval": toint(
                                                    page,
                                                    module_tx_user_refresh_login_interval_label.value,
                                                ),
                                            },
                                        }
                                    }
                                }
                            },
                        ),
                    ),
                ]

    elif page.route.split("/")[2] == "wy":
        module_wy_cookie_label = flet.TextField(
            label="cookie", value=config["module"]["wy"]["user"]["cookie"]
        )
        return [
            flet.Container(
                content=flet.Text(value="网易云音乐相关配置", size=30),
                alignment=flet.alignment.center,
            ),
            flet.Text(
                "账号cookie数据，可以通过浏览器获取，需要vip账号来获取会员歌曲，如果没有请留为空值"
            ),
            module_wy_cookie_label,
            flet.ElevatedButton("返回", on_click=lambda _: page.go("/module")),
            flet.ElevatedButton(
                "保存",
                on_click=lambda _: _Save(
                    page,
                    {
                        "module": {
                            "wy": {
                                "user": {"cookie": str(module_wy_cookie_label.value)}
                            }
                        }
                    },
                ),
            ),
        ]

    elif page.route.split("/")[2] == "mg":
        mg_user = config["module"]["mg"]["user"]
        module_mg_aversionid_label = flet.TextField(
            label="aversionid", value=mg_user["aversionid"]
        )
        module_mg_token_label = flet.TextField(label="token", value=mg_user["token"])
        module_mg_osversion_label = flet.TextField(
            label="osversion", value=mg_user["osversion"]
        )
        module_mg_useragent_label = flet.TextField(
            label="useragent", value=mg_user["useragent"]
        )

        return [
            flet.Container(
                content=flet.Text(value="咪咕音乐相关配置", size=30),
                alignment=flet.alignment.center,
            ),
            module_mg_aversionid_label,
            module_mg_token_label,
            module_mg_osversion_label,
            module_mg_useragent_label,
            flet.ElevatedButton("返回", on_click=lambda _: page.go("/module")),
            flet.ElevatedButton(
                "保存",
                on_click=lambda _: _Save(
                    page,
                    {
                        "module": {
                            "mg": {
                                "user": {
                                    "aversionid": str(module_mg_aversionid_label.value),
                                    "token": str(module_mg_token_label.value),
                                    "osversion": str(module_mg_osversion_label.value),
                                    "useragent": str(module_mg_useragent_label.value),
                                }
                            }
                        }
                    },
                ),
            ),
        ]

    elif page.route.split("/")[2] == "kw":
        if page.route.split("/")[-1] == "kw":
            module_kw_proto_label = flet.Dropdown(
                # width=100,
                options=[
                    flet.dropdown.Option("bd-api"),
                    flet.dropdown.Option("kuwodes"),
                ],
                value=config["module"]["kw"]["proto"],
            )
            return [
                flet.Container(
                    content=flet.Text(value="酷我音乐相关配置", size=30),
                    alignment=flet.alignment.center,
                ),
                flet.Text("在下方选择proto值"),
                module_kw_proto_label,
                flet.ElevatedButton(
                    "user", on_click=lambda _: page.go("/module/kw/user")
                ),
                flet.ElevatedButton(
                    "des", on_click=lambda _: page.go("/module/kw/des")
                ),
                flet.ElevatedButton("返回", on_click=lambda _: page.go("/module")),
                flet.ElevatedButton(
                    "保存",
                    on_click=lambda _: _Save(
                        page,
                        {"module": {"kw": {"proto": str(module_kw_proto_label.value)}}},
                    ),
                ),
            ]
        else:
            if page.route.split("/")[3] == "user":
                kw_user = config["module"]["kw"]["user"]
                module_kw_user_uid_label = flet.TextField(
                    label="uid", value=kw_user["uid"]
                )
                module_kw_user_token_label = flet.TextField(
                    label="token", value=kw_user["token"]
                )
                module_kw_user_device_id_label = flet.TextField(
                    label="device_id", value=kw_user["device_id"]
                )

                return [
                    flet.Container(
                        content=flet.Text(value="User", size=30),
                        alignment=flet.alignment.center,
                    ),
                    module_kw_user_uid_label,
                    module_kw_user_token_label,
                    module_kw_user_device_id_label,
                    flet.ElevatedButton(
                        "返回", on_click=lambda _: page.go("/module/kw")
                    ),
                    flet.ElevatedButton(
                        "保存",
                        on_click=lambda _: _Save(
                            page,
                            {
                                "module": {
                                    "kw": {
                                        "user": {
                                            "uid": str(module_kw_user_uid_label.value),
                                            "token": str(
                                                module_kw_user_token_label.value
                                            ),
                                            "device_id": str(
                                                module_kw_user_device_id_label.value
                                            ),
                                        }
                                    }
                                }
                            },
                        ),
                    ),
                ]
            elif page.route.split("/")[3] == "des":
                kw_des = config["module"]["kw"]["des"]
                module_kw_des_f_label = flet.TextField(label="f", value=kw_des["f"])
                module_kw_des_need_encrypt_label = flet.Checkbox(
                    label="need_encrypt", value=bool(kw_des["need_encrypt"])
                )
                module_kw_des_params_label = flet.TextField(
                    label="params", value=kw_des["params"]
                )
                module_kw_des_host_label = flet.TextField(
                    label="host", value=kw_des["host"]
                )
                module_kw_des_path_label = flet.TextField(
                    label="path", value=kw_des["path"]
                )
                module_kw_des_response_type_label = flet.Dropdown(
                    # width=100,
                    options=[
                        flet.dropdown.Option("json"),
                        flet.dropdown.Option("text"),
                    ],
                    value=kw_des["response_type"],
                )
                module_kw_des_url_json_path_label = flet.TextField(
                    label="url_json_path", value=kw_des["url_json_path"]
                )
                module_kw_des_bitrate_json_path_label = flet.TextField(
                    label="bitrate_json_path", value=kw_des["bitrate_json_path"]
                )
                module_kw_des_headers_label = flet.TextField(
                    label="headers", value=kw_des["headers"]
                )

                return [
                    flet.Container(
                        content=flet.Text(
                            value="kuwodes接口（mobi, nmobi）一类的加密相关配置",
                            size=30,
                        ),
                        alignment=flet.alignment.center,
                    ),
                    module_kw_des_f_label,
                    module_kw_des_need_encrypt_label,
                    flet.Text(
                        "param填写注释: {songId}为歌曲id, {map_quality}为map后的歌曲音质（酷我规范）, {raw_quality}为请求时的歌曲音质（LX规范）, {ext}为歌曲文件扩展名"
                    ),
                    module_kw_des_params_label,
                    module_kw_des_host_label,
                    module_kw_des_path_label,
                    flet.Text(
                        "当设置为json时会使用到下面的两个值来获取url/bitrate，如果为text，则为传统的逐行解析方式"
                    ),
                    module_kw_des_response_type_label,
                    module_kw_des_url_json_path_label,
                    module_kw_des_bitrate_json_path_label,
                    module_kw_des_headers_label,
                    flet.ElevatedButton(
                        "返回", on_click=lambda _: page.go("/module/kw")
                    ),
                    flet.ElevatedButton(
                        "保存",
                        on_click=lambda _: _Save(
                            page,
                            {
                                "module": {
                                    "kw": {
                                        "des": {
                                            "f": str(module_kw_des_f_label.value),
                                            "need_encrypt": bool(
                                                module_kw_des_need_encrypt_label.value
                                            ),
                                            "params": str(
                                                module_kw_des_params_label.value
                                            ),
                                            "host": str(module_kw_des_host_label.value),
                                            "path": str(module_kw_des_path_label.value),
                                            "response_type": str(
                                                module_kw_des_response_type_label.value
                                            ),
                                            "url_json_path": str(
                                                module_kw_des_url_json_path_label.value
                                            ),
                                            "bitrate_json_path": str(
                                                module_kw_des_bitrate_json_path_label.value
                                            ),
                                            "headers": json.loads(
                                                str(
                                                    module_kw_des_headers_label.value
                                                ).replace("'", '"')
                                            ),
                                        }
                                    }
                                }
                            },
                        ),
                    ),
                ]

    elif page.route.split("/")[2] == "cookiepool":
        if page.route.split("/")[-1] == "cookiepool":
            cookiepool = config["module"]["cookiepool"]
            # module_cookiepool_kg_label = flet.ElevatedButton(
            #     "kg", on_click=lambda _: page.go("/module/cookiepool/kg")
            # )
            # module_cookiepool_tx_label = flet.ElevatedButton(
            #     "tx", on_click=lambda _: page.go("/module/cookiepool/tx")
            # )
            # module_cookiepool_wy_label = flet.ElevatedButton(
            #     "wy", on_click=lambda _: page.go("/module/cookiepool/wy")
            # )
            # module_cookiepool_mg_label = flet.ElevatedButton(
            #     "mg", on_click=lambda _: page.go("/module/cookiepool/mg")
            # )
            # module_cookiepool_kw_label = flet.ElevatedButton(
            #     "kw", on_click=lambda _: page.go("/module/cookiepool/kw")
            # )

            module_cookiepool_kg_label = flet.TextField(
                label="kg", value=str(cookiepool["kg"])
            )
            module_cookiepool_tx_label = flet.TextField(
                label="tx", value=str(cookiepool["tx"])
            )
            module_cookiepool_wy_label = flet.TextField(
                label="wy", value=str(cookiepool["wy"])
            )
            module_cookiepool_mg_label = flet.TextField(
                label="mg", value=str(cookiepool["mg"])
            )
            module_cookiepool_kw_label = flet.TextField(
                label="kw", value=str(cookiepool["kw"])
            )
            # print(str(module_cookiepool_kg_label.value).replace("'", '"'))

            return [
                flet.Container(
                    content=flet.Text(value="Cookie Pool", size=30),
                    alignment=flet.alignment.center,
                ),
                module_cookiepool_kg_label,
                module_cookiepool_tx_label,
                module_cookiepool_wy_label,
                module_cookiepool_mg_label,
                module_cookiepool_kw_label,
                flet.ElevatedButton("返回", on_click=lambda _: page.go("/module")),
                flet.ElevatedButton(
                    "保存",
                    on_click=lambda _: _Save(
                        page,
                        {
                            "module": {
                                "cookiepool": {
                                    # 这里应该用json.loads, 但是一直报错, 索性直接用ast.literal_eval了
                                    "kg": ast.literal_eval(
                                        str(module_cookiepool_kg_label.value).replace(
                                            "'", '"'
                                        )
                                    ),
                                    "tx": ast.literal_eval(
                                        str(module_cookiepool_tx_label.value).replace(
                                            "'", '"'
                                        )
                                    ),
                                    "wy": ast.literal_eval(
                                        str(module_cookiepool_wy_label.value).replace(
                                            "'", '"'
                                        )
                                    ),
                                    "mg": ast.literal_eval(
                                        str(module_cookiepool_mg_label.value).replace(
                                            "'", '"'
                                        )
                                    ),
                                    "kw": ast.literal_eval(
                                        str(module_cookiepool_kw_label.value).replace(
                                            "'", '"'
                                        )
                                    ),
                                }
                            }
                        },
                    ),
                ),
            ]
        # else:
        #     # todo 还没写完
        #     # 想用列表一一对应的方式, 感觉也不太好, 以后重构(也许)再说吧
        #     if page.route.split("/")[3] == "kg":
        #         cookiepool_kg = config["module"]["cookiepool"]["kg"]
        #         cookiepool_kg_userid = []
        #         for i in cookiepool_kg:
        #             cookiepool_kg_userid.append(i["userid"])
        #         cookiepool_kg_token = []
        #         for i in cookiepool_kg:
        #             cookiepool_kg_token.append(i["token"])
        #         cookiepool_kg_mid = []
        #         for i in cookiepool_kg:
        #             cookiepool_kg_mid.append(i["mid"])
        #         cookiepool_kg_lite_sign_in_enable = []
        #         for i in cookiepool_kg:
        #             cookiepool_kg_lite_sign_in_enable.append(
        #                 i["lite_sign_in"]["enable"]
        #             )
        #         cookiepool_kg_lite_sign_in_interval = []
        #         for i in cookiepool_kg:
        #             cookiepool_kg_lite_sign_in_interval.append(
        #                 i["lite_sign_in"]["interval"]
        #             )
        #         cookiepool_kg_lite_sign_in_mixsongmid = []
        #         for i in cookiepool_kg:
        #             cookiepool_kg_lite_sign_in_mixsongmid.append(
        #                 i["lite_sign_in"]["mixsongmid"]["value"]
        #             )

        #         module_cookiepool_kg_userid_label = flet.TextField(
        #             label="userid", value=cookiepool_kg_userid
        #         )
        #         module_cookiepool_kg_token_label = flet.TextField(
        #             label="token", value=cookiepool_kg_token
        #         )
        #         module_cookiepool_kg_mid_label = flet.TextField(
        #             label="mid", value=cookiepool_kg_mid
        #         )
        #         module_cookiepool_kg_lite_sign_in_enable_label = flet.TextField(
        #             label="启用", value=cookiepool_kg_lite_sign_in_enable
        #         )
        #         module_cookiepool_kg_lite_sign_in_interval_label = flet.TextField(
        #             label="interval", value=cookiepool_kg_lite_sign_in_interval
        #         )
        #         module_cookiepool_kg_lite_sign_in_mixsongmid_label = flet.TextField(
        #             label="mix_songmid的获取方式, 默认auto, 可以改成一个数字手动",
        #             value=cookiepool_kg_lite_sign_in_mixsongmid,
        #         )

        #         return [
        #             flet.Container(
        #                 content=flet.Text(value="Cookie Pool KG", size=30),
        #                 alignment=flet.alignment.center,
        #             ),
        #             flet.Text("使用列表格式,请一一对应"),
        #             module_cookiepool_kg_userid_label,
        #             module_cookiepool_kg_token_label,
        #             module_cookiepool_kg_mid_label,
        #             module_cookiepool_kg_lite_sign_in_enable_label,
        #             module_cookiepool_kg_lite_sign_in_interval_label,
        #             module_cookiepool_kg_lite_sign_in_mixsongmid_label,
        #             flet.ElevatedButton(
        #                 "返回", on_click=lambda _: page.go("/module/cookiepool")
        #             ),
        #             flet.ElevatedButton(
        #                 "保存",
        #                 on_click=lambda _: _Save_Cookiepool(
        #                     page,
        #                     "kg",
        #                     {
        #                         "module": {
        #                             "cookiepool": {
        #                                 "kg": {
        #                                     "userid": json.loads(
        #                                         str(
        #                                             module_cookiepool_kg_userid_label.value
        #                                         ).replace("'", '"')
        #                                     ),
        #                                     "token": json.loads(
        #                                         str(
        #                                             module_cookiepool_kg_token_label.value
        #                                         ).replace("'", '"')
        #                                     ),
        #                                     "mid": json.loads(
        #                                         str(
        #                                             module_cookiepool_kg_mid_label.value
        #                                         ).replace("'", '"')
        #                                     ),
        #                                     "lite_sign_in_enable": json.loads(
        #                                         str(
        #                                             module_cookiepool_kg_lite_sign_in_enable_label.value
        #                                         ).replace("'", '"')
        #                                     ),
        #                                     "lite_sign_in_interval": json.loads(
        #                                         str(
        #                                             module_cookiepool_kg_lite_sign_in_interval_label.value
        #                                         ).replace("'", '"')
        #                                     ),
        #                                     "lite_sign_in_mixsongmid": json.loads(
        #                                         str(
        #                                             module_cookiepool_kg_lite_sign_in_mixsongmid_label.value
        #                                         ).replace("'", '"')
        #                                     ),
        #                                 }
        #                             }
        #                         }
        #                     },
        #                 ),
        #             ),
        #         ]
        #     else:
        #         return _404(page)

    return _404(page)


def main(page: flet.Page):
    mainKeys = list(config.keys())
    page.title = "LX Music API Server WebUI"

    def route_change(route):
        page.views.clear()
        page.scroll = "AUTO"
        page.views.append(
            flet.View(
                "/",
                [
                    flet.Container(
                        content=flet.Text(
                            "在下方配置你的config", size=30
                        ),
                        alignment=flet.alignment.center,
                    ),
                    flet.Container(
                        content=flet.Row(
                            [
                                flet.ElevatedButton(
                                    mainKeys[0],
                                    on_click=lambda _: page.go(f"/{mainKeys[0]}"),
                                ),
                                flet.ElevatedButton(
                                    mainKeys[1],
                                    on_click=lambda _: page.go(f"/{mainKeys[1]}"),
                                ),
                                flet.ElevatedButton(
                                    mainKeys[2],
                                    on_click=lambda _: page.go(f"/{mainKeys[2]}"),
                                ),
                            ],
                            alignment=flet.MainAxisAlignment.CENTER,
                        ),
                        alignment=flet.alignment.center,
                    ),
                ],
            )
        )

        if page.route.split("/")[1] in mainKeys:
            if page.route[1:] == "common":
                page.views.append(flet.View(f"/{page.route[1:]}", CommonPage(page)))
            elif page.route[1:] == "security":
                page.views.append(flet.View(f"/{page.route[1:]}", SecurityPage(page)))
            elif page.route[1:] == "module":
                page.views.append(flet.View(f"/{page.route[1:]}", ModulePage(page)))

            elif page.route.split("/")[1] == mainKeys[0]:
                page.views.append(
                    flet.View(
                        f"/{mainKeys[0]}/{page.route.split('/')[2]}",
                        CommonPageExpand(page),
                    )
                )
            elif page.route.split("/")[1] == mainKeys[1]:
                page.views.append(
                    flet.View(
                        f"/{mainKeys[1]}/{page.route.split('/')[2]}",
                        SecurityPageExpand(page),
                    )
                )
            elif page.route.split("/")[1] == mainKeys[2]:
                page.views.append(
                    flet.View(
                        f"/{mainKeys[2]}/{page.route.split('/')[2]}",
                        ModulePageExpand(page),
                    )
                )

        elif page.route != "/":
            # print(page.route)
            page.views.append(
                flet.View(
                    f"/404",
                    _404(page),
                )
            )

        page.update()

    page.on_route_change = route_change
    page.go(page.route)


if __name__ == "__main__":
    try:
        with open("config.json", "r+", encoding="utf-8") as f:
            config = json.loads(f.read())
    except:
        print("无法找到config.json,请先运行main.py生成config.json")
    flet.app(target=main)
    # flet.app(target=main, view=flet.AppView.WEB_BROWSER)
