import re
import zlib
import base64
from typing import Dict, List
from utils.http import HttpRequest
from server.exceptions import getLyricFailed


class KuwoLyricParser:
    """酷我音乐歌词解析器"""

    def __init__(self):
        self.time_exp = re.compile(r"^\[([\d:.]*)\]")
        self.exist_time_exp = re.compile(r"\[\d{1,2}:.*\d{1,4}\]")
        self.lyricx_tag = re.compile(r"^<-?\d+,-?\d+>")
        self.word_time_all = re.compile(r"<-?\d+,-?\d+(?:,-?\d+)?>")
        self.tag_line = re.compile(
            r"\[(ver|ti|ar|al|offset|by|kuwo):\s*(\S+(?:\s+\S+)*)\s*\]"
        )

        self.buf_key = b"yeelion"
        self.offset = 1
        self.offset2 = 1

    def build_params(self, music_id: int, is_get_lyricx: bool = True) -> str:
        """构建请求参数"""
        params = (
            f"user=12345,web,web,web&requester=localhost&req=1&rid=MUSIC_{music_id}"
        )
        if is_get_lyricx:
            params += "&lrcx=1"

        buf_str = params.encode("utf-8")
        output = bytearray(len(buf_str))

        i = 0
        key_len = len(self.buf_key)
        while i < len(buf_str):
            j = 0
            while j < key_len and i < len(buf_str):
                output[i] = self.buf_key[j] ^ buf_str[i]
                i += 1
                j += 1

        return base64.b64encode(output).decode("utf-8")

    def decode_lyric(self, data: bytes, is_get_lyricx: bool = True) -> str:
        """解码歌词数据"""
        if not data.startswith(b"tp=content"):
            return ""

        separator_index = data.find(b"\r\n\r\n")
        if separator_index == -1:
            return ""

        try:
            lrc_data = zlib.decompress(data[separator_index + 4 :])
        except:
            return ""

        if not is_get_lyricx:
            return lrc_data.decode("gb18030", errors="ignore")

        try:
            buf_str = base64.b64decode(lrc_data)
        except:
            return ""

        output = bytearray(len(buf_str))
        i = 0
        key_len = len(self.buf_key)
        while i < len(buf_str):
            j = 0
            while j < key_len and i < len(buf_str):
                output[i] = buf_str[i] ^ self.buf_key[j]
                i += 1
                j += 1

        return output.decode("gb18030", errors="ignore")

    def sort_lrc_arr(self, arr: List[Dict]) -> Dict:
        """排序歌词数组并分离翻译歌词"""
        lrc_set = set()
        lrc = []
        lrc_t = []
        is_lyricx = False

        for item in arr:
            if not is_lyricx and self.lyricx_tag.match(item["text"]):
                is_lyricx = True

            if item["time"] in lrc_set:
                if len(lrc) < 2:
                    continue
                t_item = lrc.pop()
                t_item["time"] = lrc[-1]["time"] if lrc else t_item["time"]
                lrc_t.append(t_item)
                lrc.append(item)
            else:
                lrc.append(item)
                lrc_set.add(item["time"])

        if not is_lyricx and len(lrc_t) > len(lrc) * 0.3 and len(lrc) - len(lrc_t) > 6:
            raise ValueError("Invalid lyric format")

        return {"lrc": lrc, "lrcT": lrc_t}

    def transform_lrc(self, tags: List[str], lrclist: List[Dict]) -> str:
        """转换歌词为字符串格式"""
        if not lrclist:
            return "\n".join(tags) + "\n暂无歌词" if tags else "暂无歌词"

        lines = [f"[{item['time']}]{item['text']}" for item in lrclist]

        if tags:
            return "\n".join(tags) + "\n" + "\n".join(lines)
        return "\n".join(lines)

    def parse_lrc(self, lrc: str) -> Dict:
        """解析LRC格式歌词"""
        lines = lrc.split("\n")
        tags = []
        lrc_arr = []

        for line in lines:
            line = line.strip()
            if self.tag_line.match(line):
                match = self.tag_line.match(line)
                if match.group(1) == "kuwo":
                    content = match.group(2)
                    if content and "][" in content:
                        content = content[: content.index("][")]
                    try:
                        value = int(content, 8)
                        self.offset = value // 10
                        self.offset2 = value % 10
                    except:
                        pass
                else:
                    tags.append(line)

        for line in lines:
            line = line.strip()
            match = self.time_exp.match(line)

            if match:
                text = self.time_exp.sub("", line).strip()
                time = match.group(1)

                if re.search(r"\.\d\d$", time):
                    time += "0"

                lrc_arr.append({"time": time, "text": text})
            elif self.tag_line.match(line) and not line.startswith("[kuwo:"):
                tags.append(line)

        try:
            lrc_info = self.sort_lrc_arr(lrc_arr)
        except ValueError:
            raise getLyricFailed("Get lyric failed")

        result = {
            "lyric": self.transform_lrc(tags, lrc_info["lrc"]),
            "tlyric": (
                self.transform_lrc(tags, lrc_info["lrcT"]) if lrc_info["lrcT"] else ""
            ),
        }

        if result["tlyric"]:
            result["tlyric"] = self.word_time_all.sub("", result["tlyric"])

        try:
            result["lxlyric"] = self.parse_lx_lyric(result["lyric"])
        except:
            result["lxlyric"] = ""

        result["lyric"] = self.word_time_all.sub("", result["lyric"])

        if not self.exist_time_exp.search(result["lyric"]):
            raise getLyricFailed("Get lyric failed")

        return result

    def parse_lx_lyric(self, lrc: str) -> str:
        """解析逐字歌词（简化版）"""
        return lrc

    def time_to_seconds(self, time_str: str) -> float:
        """将时间字符串转换为秒数 [mm:ss.ms] -> seconds"""
        if not time_str:
            return 0.0

        parts = time_str.split(":")
        if len(parts) != 2:
            return 0.0

        try:
            minutes = int(parts[0])
            seconds_parts = parts[1].split(".")
            seconds = int(seconds_parts[0])

            if len(seconds_parts) > 1:
                ms_str = seconds_parts[1].ljust(3, "0")[:3]
                milliseconds = int(ms_str)
            else:
                milliseconds = 0

            return minutes * 60 + seconds + milliseconds / 1000
        except:
            return 0.0

    def parse_lyric_by_second(self, lrc: str) -> List[Dict]:
        """解析歌词为按秒格式"""
        if not lrc:
            return []

        lines = lrc.split("\n")
        result = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = self.time_exp.match(line)
            if match:
                time_str = match.group(1)
                text = self.time_exp.sub("", line).strip()

                seconds = self.time_to_seconds(time_str)

                result.append(
                    {
                        "time": seconds,
                        "lineLyric": text,
                    }
                )

        result.sort(key=lambda x: x["time"])
        return result


class KuwoLyricFetcher:
    """酷我音乐歌词获取器"""

    def __init__(self):
        self.parser = KuwoLyricParser()

    async def get_lyric(self, music_id: int, is_get_lyricx: bool = True) -> Dict:
        """获取歌词"""
        url = f"http://newlyric.kuwo.cn/newlyric.lrc?{self.parser.build_params(music_id, is_get_lyricx)}"

        try:
            response = await HttpRequest(url)

            if response.status_code != 200:
                raise getLyricFailed(f"HTTP Error: {response.status_code}")

            decoded_lrc = self.parser.decode_lyric(response.content, is_get_lyricx)
            if not decoded_lrc:
                raise getLyricFailed("Decode lyric failed")

            return self.parser.parse_lrc(decoded_lrc)

        except getLyricFailed:
            raise
        except Exception as e:
            raise getLyricFailed(f"Get lyric failed: {str(e)}")


_fetcher = KuwoLyricFetcher()

global_parser = KuwoLyricParser()


async def getLyric(songId: int | str) -> dict:
    """获取酷我音乐歌词（兼容接口）"""
    if not str(songId).isdigit():
        raise getLyricFailed("无效的歌曲ID")

    music_id = int(songId)
    result = await _fetcher.get_lyric(music_id, is_get_lyricx=True)
    formated_second_lyric = []

    second_lyric = global_parser.parse_lyric_by_second(result.get("lyric", ""))
    for x in second_lyric:
        x["time"] = str(x["time"])
        formated_second_lyric.append(x)
        continue

    return {
        "lyric": result.get("lyric", ""),
        "tlyric": result.get("tlyric", ""),
        "rlyric": "",
        "lxlyric": result.get("lxlyric", ""),
        "second_lyric": formated_second_lyric,
    }
