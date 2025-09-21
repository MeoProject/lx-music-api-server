default = {
    "server": {
        "host": "0.0.0.0",
        "port": 9000,
        "reverse_proxy": False,
        "debug": False,
        "output_logs": True,
        "real_ip": "X-Real-IP",
        "proto": "X-Forwarded-Proto",
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
    "gcsp": {
        "enable": False,
        "package_md5": "",
        "salt_1": "NDRjZGIzNzliNzEe",
        "salt_2": "6562653262383463363633646364306534333668",
        "enable_verify": False,
    },
    "module": {
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
                    "useragent": "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ABR-AL80 Build/V417IR) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1",
                }
            ]
        },
    },
}
