import re
import zlib
import ujson
from server.exceptions import getLyricFailed
from modules.info.kg import getMusicInfo
from utils import http
from utils.url import encodeURI
from utils.base64 import createBase64Decode


class ParseTools:
    def __init__(self):
        self.head_exp = r"^.*\[id:\$\w+\]\n"

    def parse(self, string):
        string = string.replace("\r", "")
        if re.match(self.head_exp, string):
            string = re.sub(self.head_exp, "", string)
        trans = re.search(r"\[language:([\w=\\/+]+)\]", string)
        lyric = None
        rlyric = None
        tlyric = None
        if trans:
            string = re.sub(r"\[language:[\w=\\/+]+\]\n", "", string)
            decoded_trans = createBase64Decode(trans.group(1)).decode("utf-8")
            trans_json = ujson.loads(decoded_trans)
            for item in trans_json["content"]:
                if item["type"] == 0:
                    rlyric = item["lyricContent"]
                elif item["type"] == 1:
                    tlyric = item["lyricContent"]
        self.i = 0
        lxlyric = re.sub(
            r"\[((\d+),\d+)\].*",
            lambda x: self.process_lyric_match(x, rlyric, tlyric, self.i),
            string,
        )
        rlyric = "\n".join(rlyric) if rlyric else ""
        tlyric = "\n".join(tlyric) if tlyric else ""
        lxlyric = re.sub(r"<(\d+,\d+),\d+>", r"<\1>", lxlyric)
        lyric = re.sub(r"<\d+,\d+>", "", lxlyric)
        return {"lyric": lyric, "tlyric": tlyric, "rlyric": rlyric, "lxlyric": lxlyric}

    def process_lyric_match(self, match, rlyric, tlyric, i):
        result = re.match(r"\[((\d+),\d+)\].*", match.group(0))
        time = int(result.group(2))
        ms = time % 1000
        time /= 1000
        m = str(int(time / 60)).zfill(2)
        time %= 60
        s = str(int(time)).zfill(2)
        time_string = f"{m}:{s}.{ms}"
        transformed_t = ""
        if tlyric:
            for t in tlyric[i]:
                transformed_t += t
            tlyric[i] = transformed_t
        if rlyric:
            nr = []
            for r in rlyric[i]:
                nr.append(r)
            _tnr = "".join(nr)
            if " " in _tnr:
                rlyric[i] = _tnr
            else:
                nr = []
                for r in rlyric[i]:
                    nr.append(r.strip())
                rlyric[i] = " ".join(nr)
        if rlyric:
            rlyric[i] = f'[{time_string}]{rlyric[i] if rlyric[i] else ""}'.replace(
                "  ", " "
            )
        if tlyric:
            tlyric[i] = f'[{time_string}]{tlyric[i] if tlyric[i] else ""}'
        self.i += 1
        return re.sub(result.group(1), time_string, match.group(0))


global_parser = ParseTools()


def krcDecode(a: bytes):
    encrypt_key = (64, 71, 97, 119, 94, 50, 116, 71, 81, 54, 49, 45, 206, 210, 110, 105)
    content = a[4:]  # krc1
    compress_content = bytes(
        content[i] ^ encrypt_key[i % len(encrypt_key)] for i in range(len(content))
    )
    text_bytes = zlib.decompress(bytes(compress_content))
    text = text_bytes.decode("utf-8")
    return text


async def lyricSearchByHash(hash_):
    _, musicInfo = await getMusicInfo(hash_)
    if not musicInfo:
        raise getLyricFailed("歌曲信息获取失败")
    hash_new = musicInfo["audio_info"]["hash"]
    name = musicInfo["songname"]
    timelength = int(musicInfo["audio_info"]["timelength"]) // 1000
    req = await http.HttpRequest(
        encodeURI(
            f"http://lyrics.kugou.com/search?ver=1&man=yes&client=pc&keyword="
            + name
            + "&hash="
            + hash_new
            + "&timelength="
            + str(timelength)
        ),
        {
            "method": "GET",
        },
    )
    body = req.json()
    if body["status"] != 200:
        raise getLyricFailed("歌词获取失败")
    if not body["candidates"]:
        raise getLyricFailed("歌词获取失败: 当前歌曲无歌词")
    lyric = body["candidates"][0]
    return lyric["id"], lyric["accesskey"]


async def getLyric(hash_):
    try:
        lyric_id, accesskey = await lyricSearchByHash(hash_)
    except:
        raise getLyricFailed("未检索到歌词")

    req = await http.HttpRequest(
        f"http://lyrics.kugou.com/download?ver=1&client=pc&id={lyric_id}&accesskey={accesskey}",
        {
            "method": "GET",
        },
    )
    body = req.json()

    if body["status"] != 200 or body["error_code"] != 0 or (not body["content"]):
        raise getLyricFailed("歌词获取失败")

    content = createBase64Decode(body["content"])
    content = krcDecode(content)

    return global_parser.parse(content)
