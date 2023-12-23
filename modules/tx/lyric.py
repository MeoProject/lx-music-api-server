# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: lyric.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from .utils import signRequest
from .musicInfo import getMusicInfo
from common.exceptions import FailedException
from common.utils import createBase64Decode
from common import variable
from common import qdes
import re

class ParseTools:
    def __init__(self):
        self.rxps = {
            'info': re.compile(r'^{"/'),
            'lineTime': re.compile(r'^\[(\d+),\d+\]'),
            'lineTime2': re.compile(r'^\[([\d:.]+)\]'),
            'wordTime': re.compile(r'\(\d+,\d+\)'),
            'wordTimeAll': re.compile(r'(\(\d+,\d+\))'),
            'timeLabelFixRxp': re.compile(r'(?:\.0+|0+)$'),
        }

    def ms_format(self, time_ms):
        if not time_ms:
            return ''
        ms = time_ms % 1000
        time_ms /= 1000
        m = str(int(time_ms / 60)).zfill(2)
        time_ms %= 60
        s = str(int(time_ms)).zfill(2)
        return f"[{m}:{s}.{str(ms).zfill(3)}]"

    def parse_lyric(self, lrc):
        lrc = lrc.strip()
        lrc = lrc.replace('\r', '')
        if not lrc:
            return {'lyric': '', 'lxlyric': ''}
        lines = lrc.split('\n')

        lxlrc_lines = []
        lyric_lines = []

        for line in lines:
            line = line.strip()
            result = self.rxps['lineTime'].match(line)
            if not result:
                if line.startswith('[offset'):
                    lxlrc_lines.append(line)
                    lyric_lines.append(line)
                if self.rxps['lineTime2'].search(line):
                    lyric_lines.append(line)
                continue

            start_ms_time = int(result.group(1))
            start_time_str = self.ms_format(start_ms_time)
            if not start_time_str:
                continue

            words = re.sub(self.rxps['lineTime'], '', line)

            lyric_lines.append(f"{start_time_str}{re.sub(self.rxps['wordTimeAll'], '', words)}")

            times = re.findall(self.rxps['wordTimeAll'], words)
            if not times:
                continue
            times = [
                f"<{max(int(match.group(1)) - start_ms_time, 0)},{match.group(2)}>"
                for match in re.finditer(r'\((\d+),(\d+)\)', words)
            ]
            word_arr = re.split(self.rxps['wordTime'], words)
            new_words = ''.join([f"{time}{word}" for time, word in zip(times, word_arr)])
            lxlrc_lines.append(f"{start_time_str}{new_words}")

        return {
            'lyric': '\n'.join(lyric_lines),
            'lxlyric': '\n'.join(lxlrc_lines),
        }

    def parse_rlyric(self, lrc):
        lrc = lrc.strip()
        lrc = lrc.replace('\r', '')
        if not lrc:
            return {'lyric': '', 'lxlyric': ''}
        lines = lrc.split('\n')

        lyric_lines = []

        for line in lines:
            line = line.strip()
            result = self.rxps['lineTime'].match(line)
            if not result:
                continue

            start_ms_time = int(result.group(1))
            start_time_str = self.ms_format(start_ms_time)
            if not start_time_str:
                continue

            words = re.sub(self.rxps['lineTime'], '', line)

            lyric_lines.append(f"{start_time_str}{re.sub(self.rxps['wordTimeAll'], '', words)}")

        return '\n'.join(lyric_lines)

    def remove_tag(self, string):
        return re.sub(r'^[\S\s]*?LyricContent="', '', string).replace('"\/>[\S\s]*?$', '')

    def get_intv(self, interval):
        if '.' not in interval:
            interval += '.0'
        arr = re.split(':|\.', interval.ljust(8, '0'))[:3]
        m, s, ms = map(int, arr)
        return m * 3600000 + s * 1000 + ms

    def fix_rlrc_time_tag(self, rlrc, lrc):
        rlrc_lines = rlrc.split('\n')
        lrc_lines = lrc.split('\n')
        new_lrc = []
        for line in rlrc_lines:
            result = self.rxps['lineTime2'].search(line)
            if not result:
                continue
            words = re.sub(self.rxps['lineTime2'], '', line)
            if not words.strip():
                continue
            t1 = self.get_intv(result.group(1))
            while lrc_lines:
                lrc_line = lrc_lines.pop(0)
                lrc_line_result = self.rxps['lineTime2'].search(lrc_line)
                if not lrc_line_result:
                    continue
                t2 = self.get_intv(lrc_line_result.group(1))
                if abs(t1 - t2) < 100:
                    new_lrc.append(re.sub(self.rxps['lineTime2'], lrc_line_result.group(0), line))
                    break
        return '\n'.join(new_lrc)

    def fix_tlrc_time_tag(self, tlrc, lrc):
        tlrc_lines = tlrc.split('\n')
        lrc_lines = lrc.split('\n')
        new_lrc = []
        time_tag_rxp = r'^\[[\d:.]+\]'
        
        for line in tlrc_lines:
            result = re.match(time_tag_rxp, line)
            if not result:
                continue
            words = re.sub(time_tag_rxp, '', line)
            if not words.strip():
                continue
            tag = re.sub(r'\[\d+:\d+\.\d+\]', '', result.group(0))

            while lrc_lines:
                lrc_line = lrc_lines.pop(0)
                lrc_line_result = re.match(time_tag_rxp, lrc_line)
                if not lrc_line_result:
                    continue
                if tag in lrc_line_result.group(0):
                    new_lrc.append(re.sub(time_tag_rxp, lrc_line_result.group(0), line))
                    break
        
        return '\n'.join(new_lrc)

    def parse(self, lrc, tlrc, rlrc):
        info = {
            'lyric': '',
            'tlyric': '',
            'rlyric': '',
            'lxlyric': '',
        }
        if lrc:
            lyric_info = self.parse_lyric(self.remove_tag(lrc))
            info['lyric'] = lyric_info['lyric']
            info['lxlyric'] = lyric_info['lxlyric']
        if rlrc:
            info['rlyric'] = self.fix_rlrc_time_tag(self.parse_rlyric(self.remove_tag(rlrc)), info['lyric'])
        if tlrc:
            info['tlyric'] = self.fix_tlrc_time_tag(tlrc, info['lyric'])

        return info

global_parser = ParseTools()

def parseLyric(l, t = '', r = ''):
    return global_parser.parse(l, t, r)

async def getLyric(songId):
    # mid and Numberid
    if (re.match("^[0-9]+$", str(songId))):
        songId = int(songId)
    else:
        try:
            getNumberIDRequest = await getMusicInfo(songId)
        except:
            raise FailedException('歌曲信息获取失败')
        songId = getNumberIDRequest['track_info']['id']
    req = await signRequest({
        "comm": {
            "ct": '19',
            "cv": '1859',
            "uin": '0',
        },
        "req": {
            "method": 'GetPlayLyricInfo',
            "module": 'music.musichallSong.PlayLyricInfo',
            "param": {
                "format": 'json',
                "crypt": 1 if variable.qdes_lib_loaded else 0,
                "ct": 19,
                "cv": 1873,
                "interval": 0,
                "lrc_t": 0,
                "qrc": 1 if variable.qdes_lib_loaded else 0,
                "qrc_t": 0,
                "roma": 1 if variable.qdes_lib_loaded else 0,
                "roma_t": 0,
                "songID": songId,
                "trans": 1,
                "trans_t": 0,
                "type": -1,
            }
        }
    })
    body = req.json()
    if ((body['code'] != 0) or (body['req']['code'] != 0)):
        raise FailedException('歌词获取失败')
    if (variable.qdes_lib_loaded):
        l = body['req']['data']['lyric']
        t = body['req']['data']['trans']
        r = body['req']['data']['roma']
        if (l.startswith('789C') and len(l) < 200): # unsupported format
            raise FailedException('纯音乐短歌词不受支持')
        dl = qdes.qdes_decrypt(l)
        if (t):
            dt = qdes.qdes_decrypt(t)
        else:
            dt = ''
        if (r):
            dr = qdes.qdes_decrypt(r)
        else:
            dr = ''
        return global_parser.parse(dl, dt, dr)
    else: # 不获取QRC时的歌词不被加密，解码base64，不进行parse，不支持逐字和罗马音，歌词数据没有毫秒
        l = body['req']['data']['lyric']
        t = body['req']['data']['trans']
        return {
            'lyric': createBase64Decode(l).decode('utf-8'),
            'tlyric': createBase64Decode(t).decode('utf-8'),
            'rlyric': '',
            'lxlyric': '',
        }
