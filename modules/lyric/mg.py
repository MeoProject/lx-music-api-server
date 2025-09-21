import re
from server.exceptions import getLyricFailed
from modules.plat.mg.mrc import decrypt
from utils.http import HttpRequest
from typing import Dict, Optional, Any


class MrcTools:
    def __init__(self):
        self.rxps = {
            "lineTime": re.compile(r"^\s*\[(\d+),\d+\]"),
            "wordTime": re.compile(r"\(\d+,\d+\)"),
            "wordTimeAll": re.compile(r"(\(\d+,\d+\))"),
        }

    def parse_lyric(self, text: str) -> Dict[str, str]:
        text = text.replace("\r", "")
        lines = text.split("\n")
        lxlrc_lines = []
        lrc_lines = []
        for line in lines:
            if len(line) < 6:
                continue
            result = self.rxps["lineTime"].search(line)
            if not result:
                continue
            start_time = int(result.group(1))
            time = start_time
            ms = time % 1000
            time //= 1000
            m = str(time // 60).zfill(2)
            time %= 60
            s = str(int(time)).zfill(2)
            formatted_time = f"{m}:{s}.{ms}"
            words = self.rxps["lineTime"].sub("", line)
            clean_words = self.rxps["wordTimeAll"].sub("", words)
            lrc_lines.append(f"[{formatted_time}]{clean_words}")
            times = self.rxps["wordTimeAll"].findall(words)
            if not times:
                continue
            converted_times = []
            for time_str in times:
                time_match = re.search(r"\((\d+),(\d+)\)", time_str)
                if time_match:
                    relative_time = int(time_match.group(1)) - start_time
                    duration = time_match.group(2)
                    converted_times.append(f"<{relative_time},{duration}>")
            word_arr = self.rxps["wordTime"].split(words)
            new_words = "".join(
                f"{time}{word}" for time, word in zip(converted_times, word_arr) if word
            )
            lxlrc_lines.append(f"[{formatted_time}]{new_words}")
        return {"lyric": "\n".join(lrc_lines), "lxlyric": "\n".join(lxlrc_lines)}

    async def get_text(self, url: str) -> str:
        headers = {
            "Referer": "https://app.c.nf.migu.cn/",
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
            "channel": "0146921",
        }
        response = await HttpRequest(url, {"method": "GET", "headers": headers})
        if response.status_code != 200:
            raise getLyricFailed(response.text)
        return response.text

    async def get_mrc(self, url: str) -> Dict[str, str]:
        text = await self.get_text(url)
        decrypted_text = decrypt(text)
        return self.parse_lyric(decrypted_text)

    async def get_lrc(self, url: str) -> Dict[str, str]:
        text = await self.get_text(url)
        return {"lxlyric": "", "lyric": text}

    async def get_trc(self, url: Optional[str]) -> str:
        if not url:
            return ""
        return await self.get_text(url)

    async def get_lyric(self, info: Dict[str, Any]) -> Dict[str, str]:
        try:
            if info.get("mrcUrl"):
                lyric_info = await self.get_mrc(info["mrcUrl"])
            elif info.get("lrcUrl"):
                lyric_info = await self.get_lrc(info["lrcUrl"])
            else:
                raise getLyricFailed("获取歌词失败")
            tlyric = await self.get_trc(info.get("trcUrl"))
            lyric_info["tlyric"] = tlyric
            return lyric_info
        except getLyricFailed:
            raise getLyricFailed("获取歌词失败")
