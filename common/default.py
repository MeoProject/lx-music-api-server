default = {
    "common": {
        "binds": [
            {
                "port": "8000",
                "scheme": "http",
                "ssl_cert_path": "",
                "ssl_key_path": "",
            },
        ],
        "reverse_proxy": {
            "allow_public_ip": True,
            "allow_proxy": True,
            "real_ip_header": "X-Real-IP",
            "real_host_header": "X-Real-Host",
        },
        "debug_mode": False,
        "log_file": True,
        "download_config": {
            "name": "替换为音源名称",
            "intro": "替换为音源简介",
            "author": "替换为音源作者",
            "version": "替换为音源版本",
            "filename": "lx-music-source.js",
            "dev": False,
            "update": True,
            "updateMsg": "⚠️ 重要更新\n更新地址:\n{updateUrl}\n",
            "quality": {
                "kw": ["128k", "320k", "flac", "flac24bit", "hires"],
                "mg": ["128k", "320k", "flac", "flac24bit", "hires"],
                "kg": ["128k", "320k", "flac", "flac24bit", "hires", "atmos", "master"],
                "tx": [
                    "128k",
                    "320k",
                    "flac",
                    "flac24bit",
                    "hires",
                    "atmos",
                    "atmos_plus",
                    "master",
                ],
                "wy": ["128k", "320k", "flac", "flac24bit", "hires", "atmos", "master"],
            },
        },
        "cache": {
            "enable": True,
            "redis": {
                "host": "127.0.0.1",
                "port": "6379",
                "db": "0",
                "user": "",
                "password": "",
                "key_prefix": "MUSIC_API",
            },
        },
    },
    "security": {
        "key": {"enable": True, "list": ["114514"]},
        "banlist": {"enable": True},
    },
    "gcsp": {
        "package_md5": "",
        "salt_1": "",
        "salt_2": "",
        "enable_verify": False,
        "enable_source": ["kw", "kg", "tx", "wy", "mg"],
    },
    "module": {
        "kw": {
            "source_config_list": [
                {
                    "type": "mobi",
                    "source": "",
                    "isenc": False,
                    "params": {
                        "f": "web",
                        "rid": "{songId}",
                        "br": "{mapQuality}",
                        "type": "convert_url_with_sign",
                        "surl": 1,
                    },
                },
                {
                    "type": "nmobi",
                    "source": "",
                    "isenc": False,
                    "params": {
                        "f": "web",
                        "rid": "{songId}",
                        "br": "{mapQuality}",
                        "type": "convert_url_with_sign",
                        "surl": 1,
                    },
                },
            ]
        },
        "kg": {
            "mid": ["nezha"],
            "users": [
                {
                    "userid": "",
                    "token": "",
                    "version": "offcial",
                    "refresh_login": True,
                },
            ],
        },
        "tx": {
            "users": [
                {
                    "uin": "",
                    "token": "",
                    "openId": "",
                    "accessToken": "",
                    "refreshToken": "",
                    "refreshKey": "",
                    "vip_type": "",
                    "refresh_login": True,
                    "devices": {
                        "QIMEI": "",
                        "model": "",
                        "osver": "",
                        "level": "",
                        "fingerprint": "",
                        "UDID": "",
                        "UDID2": "",
                        "aid": "",
                    },
                },
            ],
            "cdnaddr": "https://wx.music.tc.qq.com/",
        },
        "wy": {"users": [{"cookie": ""}]},
        "mg": {
            "users": [
                {
                    "ce": "",
                    "token": "",
                    "channel": "014000D",
                    "useragent": "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ABR-AL80 Build/V417IR) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1",
                }
            ]
        },
    },
}
