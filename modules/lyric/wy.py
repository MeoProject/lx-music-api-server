import re
import math
from utils import orjson
from modules.plat.wy import eEncrypt
from utils.http import HttpRequest
from server.exceptions import getLyricFailed


class ParseTools:
    def __init__(self):
        self.rxps = {
            "info": re.compile(r'^{"'),
            "line_time": re.compile(r"^\[(\d+),\d+\]"),
            "word_time": re.compile(r"\(\d+,\d+,\d+\)"),
            "word_time_all": re.compile(r"(\(\d+,\d+,\d+\))"),
        }

    def ms_format(self, time_ms):
        """将毫秒时间格式化为歌词时间标签格式"""
        try:
            time_ms = int(time_ms)
        except (ValueError, TypeError):
            return ""

        if math.isnan(time_ms):
            return ""

        ms = time_ms % 1000
        time_ms //= 1000
        m = str(time_ms // 60).zfill(2)
        time_ms %= 60
        s = str(int(time_ms)).zfill(2)
        return f"[{m}:{s}.{ms}]"

    def parse_lyric(self, lines):
        """解析歌词行，生成普通歌词和逐字歌词"""
        lxlrc_lines = []
        lrc_lines = []

        for line in lines:
            line = line.strip()
            result = self.rxps["line_time"].match(line)

            if not result:
                if line.startswith("[offset"):
                    lxlrc_lines.append(line)
                    lrc_lines.append(line)
                continue

            start_ms_time = int(result.group(1))
            start_time_str = self.ms_format(start_ms_time)
            if not start_time_str:
                continue

            words = self.rxps["line_time"].sub("", line)

            # 生成普通歌词（去除时间标记）
            lrc_lines.append(
                f"{start_time_str}{self.rxps['word_time_all'].sub('', words)}"
            )

            # 处理逐字歌词
            times = self.rxps["word_time_all"].findall(words)
            if not times:
                continue

            # 转换时间格式
            converted_times = []
            for time in times:
                match = re.match(r"\((\d+),(\d+),\d+\)", time)
                if match:
                    time_offset = max(int(match.group(1)) - start_ms_time, 0)
                    duration = match.group(2)
                    converted_times.append(f"<{time_offset},{duration}>")

            # 分割词组
            word_arr = self.rxps["word_time"].split(words)
            if word_arr:
                word_arr.pop(0)  # 移除第一个空元素

            # 组合逐字歌词
            new_words = "".join(
                f"{time}{word}" for time, word in zip(converted_times, word_arr)
            )
            lxlrc_lines.append(f"{start_time_str}{new_words}")

        return {"lyric": "\n".join(lrc_lines), "lxlyric": "\n".join(lxlrc_lines)}

    def parse_header_info(self, str_content):
        """解析歌词头部信息"""
        str_content = str_content.strip()
        str_content = str_content.replace("\r", "")

        if not str_content:
            return None

        lines = str_content.split("\n")
        result_lines = []

        for line in lines:
            if not self.rxps["info"].match(line):
                result_lines.append(line)
            else:
                try:
                    info = orjson.loads(line)
                    time_tag = self.ms_format(info.get("t", 0))
                    if time_tag:
                        text = "".join(t.get("tx", "") for t in info.get("c", []))
                        result_lines.append(f"{time_tag}{text}")
                    else:
                        result_lines.append("")
                except:
                    result_lines.append("")

        return result_lines

    def get_intv(self, interval):
        """将时间字符串转换为毫秒"""
        if not interval:
            return 0

        if "." not in interval:
            interval += ".0"

        arr = interval.split(":")
        if len(arr) == 2:
            # 格式: mm:ss.ms
            m_s, ms = arr[1].split(".")
            m = arr[0]
            s = m_s
        else:
            # 格式: ss.ms
            s, ms = interval.split(".")
            m = "0"

        return int(m) * 60000 + int(s) * 1000 + int(ms)

    def fix_time_tag(self, lrc, targetlrc):
        """修正时间标签，使歌词行对齐"""
        lrc_lines = lrc.split("\n")
        targetlrc_lines = targetlrc.split("\n")
        time_rxp = re.compile(r"^\[([\d:.]+)\]")
        temp = []
        new_lrc = []

        for line in targetlrc_lines:
            result = time_rxp.match(line)
            if not result:
                continue

            words = time_rxp.sub("", line)
            if not words.strip():
                continue

            t1 = self.get_intv(result.group(1))

            while lrc_lines:
                lrc_line = lrc_lines.pop(0)
                lrc_line_result = time_rxp.match(lrc_line)

                if not lrc_line_result:
                    continue

                t2 = self.get_intv(lrc_line_result.group(1))

                if abs(t1 - t2) < 100:
                    lrc = time_rxp.sub(lrc_line_result.group(0), line).strip()
                    if lrc:
                        new_lrc.append(lrc)
                    break

                temp.append(lrc_line)

            lrc_lines = temp + lrc_lines
            temp = []

        return "\n".join(new_lrc)

    def parse(self, ylrc, ytlrc, yrlrc, lrc, tlrc, rlrc):
        """解析所有歌词类型"""
        info = {"lyric": "", "tlyric": "", "rlyric": "", "lxlyric": ""}

        if ylrc:
            lines = self.parse_header_info(ylrc)
            if lines:
                result = self.parse_lyric(lines)

                # 处理翻译歌词
                if ytlrc:
                    t_lines = self.parse_header_info(ytlrc)
                    if t_lines:
                        info["tlyric"] = self.fix_time_tag(
                            result["lyric"], "\n".join(t_lines)
                        )

                # 处理罗马音歌词
                if yrlrc:
                    r_lines = self.parse_header_info(yrlrc)
                    if r_lines:
                        info["rlyric"] = self.fix_time_tag(
                            result["lyric"], "\n".join(r_lines)
                        )

                # 提取时间标签头部
                time_rxp = re.compile(r"^\[[\d:.]+\]")
                headers = "\n".join(l for l in lines if time_rxp.match(l))
                info["lyric"] = f"{headers}\n{result['lyric']}"
                info["lxlyric"] = result["lxlyric"]
                return info

        # 处理普通歌词
        if lrc:
            lines = self.parse_header_info(lrc)
            if lines:
                info["lyric"] = "\n".join(lines)

        # 处理翻译歌词
        if tlrc:
            lines = self.parse_header_info(tlrc)
            if lines:
                info["tlyric"] = "\n".join(lines)

        # 处理罗马音歌词
        if rlrc:
            lines = self.parse_header_info(rlrc)
            if lines:
                info["rlyric"] = "\n".join(lines)

        return info


parser = ParseTools()


def fixTimeLabel(lrc, tlrc, romalrc):
    """修正时间标签格式"""
    if lrc:
        # 将 [mm:ss:ms] 格式转换为 [mm:ss.ms]
        new_lrc = re.sub(r"\[(\d{2}:\d{2}):(\d{2})\]", r"[\1.\2]", lrc)
        new_tlrc = (
            re.sub(r"\[(\d{2}:\d{2}):(\d{2})\]", r"[\1.\2]", tlrc) if tlrc else tlrc
        )

        if new_lrc != lrc or new_tlrc != tlrc:
            lrc = new_lrc
            tlrc = new_tlrc

            if romalrc:
                romalrc = re.sub(r"\[(\d{2}:\d{2}):(\d{2,3})\]", r"[\1.\2]", romalrc)
                romalrc = re.sub(r"\[(\d{2}:\d{2}\.\d{2})0\]", r"[\1]", romalrc)

    return {"lrc": lrc, "tlrc": tlrc, "romalrc": romalrc}


async def getLyric(songId):
    path = "/api/song/lyric/v1"
    url = "http://interface3.music.163.com/eapi/song/lyric/v1"
    params = {
        "id": songId,
        "cp": False,
        "tv": 0,
        "lv": 0,
        "rv": 0,
        "kv": 0,
        "yv": 0,
        "ytv": 0,
        "yrv": 0,
    }

    req = await HttpRequest(
        url,
        {
            "method": "POST",
            "form": eEncrypt(path, params),
        },
    )
    body = req.json()

    if (body["code"] != 200) or (not body["lrc"]["lyric"]):
        raise getLyricFailed("歌词获取失败")

    fixTimeLabelLrc = fixTimeLabel(
        body["lrc"]["lyric"],
        body.get("tlyric", {}).get("lyric"),
        body.get("romalrc", {}).get("lyric"),
    )

    return parser.parse(
        body.get("yrc", {}).get("lyric"),
        body.get("ytlrc", {}).get("lyric"),
        body.get("yromalrc", {}).get("lyric"),
        fixTimeLabelLrc["lrc"],
        fixTimeLabelLrc["tlrc"],
        fixTimeLabelLrc["romalrc"],
    )
