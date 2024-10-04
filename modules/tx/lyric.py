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

    def msFormat(self, timeMs):
        if isinstance(timeMs, float) and timeMs.is_nan():
            return ''
        ms = timeMs % 1000
        timeMs //= 1000
        m = str(int(timeMs // 60)).zfill(2)
        s = str(int(timeMs % 60)).zfill(2)
        return f'[{m}:{s}.{str(ms).zfill(3)}]'

    def parseLyric(self, lrc):
        lrc = lrc.strip().replace('\r', '')
        if not lrc:
            return {'lyric': '', 'lxlyric': ''}
        # print(lrc)
        
        lines = lrc.split('\n')
        lxlrcLines = []
        lrcLines = []

        for line in lines:
            line = line.strip()
            result = self.rxps['lineTime'].match(line)
            if not result:
                if line.startswith('[offset'):
                    lxlrcLines.append(line)
                    lrcLines.append(line)
                if self.rxps['lineTime2'].match(line):
                    lrcLines.append(line)
                continue

            startMsTime = int(result.group(1))
            startTimeStr = self.msFormat(startMsTime)
            if not startTimeStr:
                continue

            words = re.sub(self.rxps['lineTime'], '', line)

            lrcLines.append(f'{startTimeStr}{re.sub(self.rxps["wordTimeAll"], "", words)}')

            times = re.findall(self.rxps['wordTimeAll'], words)
            if not times:
                continue
            _rxp = r"\((\d+),(\d+)\)"
            times = [f'''<{max(int(re.search(_rxp, time).group(1)) - startMsTime, 0)},{re.search(_rxp, time).group(2)}>''' for time in times]
            wordArr = re.split(self.rxps['wordTime'], words)
            newWords = ''.join([f'{time}{wordArr[index]}' for index, time in enumerate(times)])
            lxlrcLines.append(f'{startTimeStr}{newWords}')

        return {
            'lyric': '\n'.join(lrcLines),
            'lxlyric': '\n'.join(lxlrcLines),
        }

    def parseRlyric(self, lrc):
        lrc = lrc.strip().replace('\r', '')
        if not lrc:
            return {'lyric': '', 'lxlyric': ''}

        lines = lrc.split('\n')
        lrcLines = []

        for line in lines:
            line = line.strip()
            result = self.rxps['lineTime'].match(line)
            if not result:
                continue

            startMsTime = int(result.group(1))
            startTimeStr = self.msFormat(startMsTime)
            if not startTimeStr:
                continue

            words = re.sub(self.rxps['lineTime'], '', line)
            lrcLines.append(f'{startTimeStr}{re.sub(self.rxps["wordTimeAll"], "", words)}')

        return '\n'.join(lrcLines)

    def removeTag(self, string):
        return re.sub(r'^[\S\s]*?LyricContent="', '', string).replace('"\/>[\S\s]*?$', '')

    def getIntv(self, interval):
        if not interval:
            return 0
        if '.' not in interval:
            interval += '.0'
        arr = re.split(r':|\.', interval)
        while len(arr) < 3:
            arr.insert(0, '0')
        m, s, ms = arr
        return int(m) * 3600000 + int(s) * 1000 + int(ms)

    def fixRlrcTimeTag(self, rlrc, lrc):
        rlrcLines = rlrc.split('\n')
        lrcLines = lrc.split('\n')
        newLrc = []

        for line in rlrcLines:
            result = self.rxps['lineTime2'].match(line)
            if not result:
                continue
            words = re.sub(self.rxps['lineTime2'], '', line)
            if not words.strip():
                continue
            t1 = self.getIntv(result.group(1))

            while lrcLines:
                lrcLine = lrcLines.pop(0)
                lrcLineResult = self.rxps['lineTime2'].match(lrcLine)
                if not lrcLineResult:
                    continue
                t2 = self.getIntv(lrcLineResult.group(1))
                if abs(t1 - t2) < 100:
                    newLrc.append(re.sub(self.rxps['lineTime2'], lrcLineResult.group(0), line))
                    break

        return '\n'.join(newLrc)

    def fixTlrcTimeTag(self, tlrc, lrc):
        tlrcLines = tlrc.split('\n')
        lrcLines = lrc.split('\n')
        newLrc = []

        for line in tlrcLines:
            result = self.rxps['lineTime2'].match(line)
            if not result:
                continue
            words = re.sub(self.rxps['lineTime2'], '', line)
            if not words.strip():
                continue
            time = result.group(1)
            if '.' in time:
                time += '0' * (3 - len(time.split('.')[1]))

            t1 = self.getIntv(time)

            while lrcLines:
                lrcLine = lrcLines.pop(0)
                lrcLineResult = self.rxps['lineTime2'].match(lrcLine)
                if not lrcLineResult:
                    continue
                t2 = self.getIntv(lrcLineResult.group(1))
                if abs(t1 - t2) < 100:
                    newLrc.append(re.sub(self.rxps['lineTime2'], lrcLineResult.group(0), line))
                    break

        return '\n'.join(newLrc)

    def parse(self, lrc, tlrc=None, rlrc=None):
        info = {
            'lyric': '',
            'tlyric': '',
            'rlyric': '',
            'lxlyric': '',
        }

        if lrc:
            parsed_lrc = self.parseLyric(self.removeTag(lrc))
            info['lyric'] = parsed_lrc['lyric']
            info['lxlyric'] = parsed_lrc['lxlyric']

        if rlrc:
            info['rlyric'] = self.fixRlrcTimeTag(self.parseRlyric(self.removeTag(rlrc)), info['lyric'])

        if tlrc:
            info['tlyric'] = self.fixTlrcTimeTag(tlrc, info['lyric'])

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
