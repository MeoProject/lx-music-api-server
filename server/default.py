default = {
    "server": {
        "host": "0.0.0.0",
        "port": 9000,
        "debug": False,
        "reload": False,
        "workers": 1,
        "output_logs": True,
        "reverse_proxy": False,
        "real_ip": "X-Real-IP",
        "proto": "X-Forwarded-Proto",
        "link": "http://127.0.0.1:8000",
    },
    "cache": {
        "enable": False,
        "host": "127.0.0.1",
        "port": "6379",
        "db": "0",
        "user": "",
        "password": "",
        "key_prefix": "LX_API",
    },
    "script": {
        "name": "名字",
        "intro": "详情",
        "author": "作者",
        "version": "版本",
        "file": "lx-music-source.js",
        "dev": False,
        "update": False,
        "updateMsg": "{updateUrl}",
        "qualitys": {
            "kw": ["128k", "320k", "flac", "hires"],
            "kg": ["128k", "320k", "flac", "hires"],
            "tx": ["128k", "320k", "flac", "hires"],
            "wy": ["128k", "320k", "flac", "hires"],
            "mg": ["128k", "320k", "flac", "hires"],
        },
    },
    "security": {"key_verify": {"enable": False, "list": [""]}},
    "module": {
        "gcsp": {
            "enable": False,
            "package_md5": "",
            "salt_1": "NDRjZGIzNzliNzEe",
            "salt_2": "6562653262383463363633646364306534333668",
            "enable_verify": False,
        },
        "qmc_decrypter": False,
        "platform": {
            "kw": {"source_list": ["kwplayer_version_code"]},
            "kg": {
                "users": [
                    {
                        "userid": "0",
                        "token": "",
                        "refresh_login": False,
                    },
                ],
            },
            "tx": {
                "users": [
                    {
                        "uin": "0",
                        "token": "",
                        "refreshKey": "",
                        "openId": "",
                        "accessToken": "",
                        "vip_type": "normal",
                        "refresh_login": False,
                    }
                ],
                "cdnaddr": "http://wx.music.tc.qq.com/",
            },
            "wy": {"users": [{"cookie": ""}]},
            "mg": {
                "users": [
                    {
                        "ce": "",
                        "token": "",
                        "channel": "014000D",
                    }
                ]
            },
        },
    },
}
