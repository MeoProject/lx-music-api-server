# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: QMWSign.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from common.utils import md5 as _md5
import re as _re

def v(b):
    res = []
    p = [21, 4, 9, 26, 16, 20, 27, 30]
    for x in p:
        res.append(b[x])
    return ''.join(res)

def c(b):
    res = []
    p = [18, 11, 3, 2, 1, 7, 6, 25]
    for x in p:
        res.append(b[x])
    return ''.join(res)

def y(a, b, c):
    e = []
    r25 = a >> 2
    if b is not None and c is not None:
        r26 = a & 3
        r26_2 = r26 << 4
        r26_3 = b >> 4
        r26_4 = r26_2 | r26_3
        r27 = b & 15
        r27_2 = r27 << 2
        r27_3 = r27_2 | (c >> 6)
        r28 = c & 63
        e.append(r25)
        e.append(r26_4)
        e.append(r27_3)
        e.append(r28)
    else:
        r10 = a >> 2
        r11 = a & 3
        r11_2 = r11 << 4
        e.append(r10)
        e.append(r11_2)
    return e

def n(ls):
    e = []
    for i in range(0, len(ls), 3):
        if i < len(ls) - 2:
            e += y(ls[i], ls[i + 1], ls[i + 2])
        else:
            e += y(ls[i], None, None)
    res = []
    b64all = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    for i in e:
        res.append(b64all[i])
    return ''.join(res)

def t(b):
    zd = {
        "0": 0,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "A": 10,
        "B": 11,
        "C": 12,
        "D": 13,
        "E": 14,
        "F": 15
    }
    ol = [212, 45, 80, 68, 195, 163, 163, 203, 157, 220, 254, 91, 204, 79, 104, 6]
    res = []
    j = 0
    for i in range(0, len(b), 2):
        one = zd[b[i]]
        two = zd[b[i + 1]]
        r = one * 16 ^ two
        res.append(r ^ ol[j])
        j += 1
    return res

def sign(params):
    md5Str = _md5(params).upper()
    h = v(md5Str)
    e = c(md5Str)
    ls = t(md5Str)
    m = n(ls)
    res = 'zzb' + h + m + e
    res = res.lower()
    r = _re.compile(r'[\\/+]')
    res = _re.sub(r, '', res)
    return res
