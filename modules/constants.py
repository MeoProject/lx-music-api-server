sourceNameTranslate = {
    "kw": "酷我音乐",
    "tx": "QQ音乐",
    "kg": "酷狗音乐",
    "wy": "网易云音乐",
    "mg": "咪咕音乐",
}

Source_Quality_Map = {
    "kw": [
        "128k",
        "320k",
        "flac",
        "hires",
        "atmos",
        "atmos_plus",
        "master",
    ],
    "kg": [
        "128k",
        "320k",
        "flac",
        "hires",
        "atmos",
        "master",
    ],
    "tx": [
        "128k",
        "320k",
        "flac",
        "hires",
        "atmos",
        "atmos_plus",
        "master",
    ],
    "wy": ["128k", "320k", "flac", "hires", "atmos", "master"],
    "mg": ["128k", "320k", "flac", "hires"],
}

QualityNameTranslate = {
    "99k": "标准音质 99K",
    "100k": "标准音质 100K",
    "128k": "标准音质 128K",
    "256k": "标准音质 256K",
    "192k": "标准音质 192K",
    "320k": "高品音质 320K",
    "flac": "无损音质 FLAC",
    "hires": "无损音质 24Bit",
    "master": "臻品母带",
    "viper_clear": "蝰蛇超清",
    "viper_atmos": "蝰蛇全景声",
    "dolby": "杜比全景声",
    "atmos": "臻品全景声",
    "atmos_plus": "臻品全景声2.0",
}

sourceExpirationTime = {
    "tx": {
        "expire": True,
        "time": 80400,
    },
    "kg": {
        "expire": True,
        "time": 24 * 60 * 60,
    },
    "kw": {
        "expire": True,
        "time": 60 * 60,
    },
    "wy": {
        "expire": True,
        "time": 12 * 60,
    },
    "mg": {
        "expire": False,
        "time": 0,
    },
}
