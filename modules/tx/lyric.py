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
        for line in tlrc_lines:
            result = self.rxps['lineTime2'].search(line)
            if not result:
                continue
            words = re.sub(self.rxps['lineTime2'], '', line)
            if not words.strip():
                continue
            time = result.group(1)
            if '.' in time:
                time += ''.ljust(3 - len(time.split('.')[1]), '0')
            t1 = self.get_intv(time)
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
