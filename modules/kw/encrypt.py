# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: kwdes.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

# KuwoDES加密实现，CV过来的，不进行注释
# 下方为原文件版权声明，在此进行保留
# Copyright (C) 2014 LiuLang <gsushzhsosgsu@gmail.com>
# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

import base64

DES_MODE_DECRYPT = 1

arrayE = [
    31, 0, DES_MODE_DECRYPT, 2, 3, 4, -1, -1, 3, 4, 5, 6, 7, 8, -1, -1, 7, 8, 9, 10, 11, 12, -1, -1, 11, 12, 13, 14, 15, 16, -1, -
    1, 15, 16, 17, 18, 19, 20, -1, -1, 19, 20, 21, 22, 23, 24, -1, -
    1, 23, 24, 25, 26, 27, 28, -1, -1, 27, 28, 29, 30, 31, 30, -1, -1
]

arrayIP = [
    57, 49, 41, 33, 25, 17, 9, DES_MODE_DECRYPT, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7, 56, 48, 40, 32, 24, 16, 8, 0, 58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6
]

arrayIP_1 = [
    39, 7, 47, 15, 55, 23, 63, 31, 38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53, 21, 61, 29, 36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27, 34, 2, 42, 10, 50, 18, 58, 26, 33, DES_MODE_DECRYPT, 41, 9, 49, 17, 57, 25, 32, 0, 40, 8, 48, 16, 56, 24
]
arrayLs = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
arrayLsMask = [0, 0x100001, 0x300003]
arrayMask = [2 ** i for i in range(64)]
arrayMask[-1] *= -1
arrayP = [
    15,  6, 19, 20, 28, 11, 27, 16,
    0, 14, 22, 25,  4, 17, 30,  9,
    1,  7, 23, 13, 31, 26,  2,  8,
    18, 12, 29,  5, 21, 10,  3, 24,
]
arrayPC_1 = [
    56, 48, 40, 32, 24, 16,  8,  0,
    57, 49, 41, 33, 25, 17,  9,  1,
    58, 50, 42, 34, 26, 18, 10,  2,
    59, 51, 43, 35, 62, 54, 46, 38,
    30, 22, 14,  6, 61, 53, 45, 37,
    29, 21, 13,  5, 60, 52, 44, 36,
    28, 20, 12,  4, 27, 19, 11,  3,
]
arrayPC_2 = [
    13, 16, 10, 23,  0,  4, -1, -1,
    2, 27, 14,  5, 20,  9, -1, -1,
    22, 18, 11,  3, 25,  7, -1, -1,
    15,  6, 26, 19, 12,  1, -1, -1,
    40, 51, 30, 36, 46, 54, -1, -1,
    29, 39, 50, 44, 32, 47, -1, -1,
    43, 48, 38, 55, 33, 52, -1, -1,
    45, 41, 49, 35, 28, 31, -1, -1,
]
matrixNSBox = [[
    14,  4,  3, 15,  2, 13,  5,  3,
    13, 14,  6,  9, 11,  2,  0,  5,
    4,  1, 10, 12, 15,  6,  9, 10,
    1,  8, 12,  7,  8, 11,  7,  0,
    0, 15, 10,  5, 14,  4,  9, 10,
    7,  8, 12,  3, 13,  1,  3,  6,
    15, 12,  6, 11,  2,  9,  5,  0,
    4,  2, 11, 14,  1,  7,  8, 13, ], [
    15,  0,  9,  5,  6, 10, 12,  9,
    8,  7,  2, 12,  3, 13,  5,  2,
    1, 14,  7,  8, 11,  4,  0,  3,
    14, 11, 13,  6,  4,  1, 10, 15,
    3, 13, 12, 11, 15,  3,  6,  0,
    4, 10,  1,  7,  8,  4, 11, 14,
    13,  8,  0,  6,  2, 15,  9,  5,
    7,  1, 10, 12, 14,  2,  5,  9, ], [
    10, 13,  1, 11,  6,  8, 11,  5,
    9,  4, 12,  2, 15,  3,  2, 14,
    0,  6, 13,  1,  3, 15,  4, 10,
    14,  9,  7, 12,  5,  0,  8,  7,
    13,  1,  2,  4,  3,  6, 12, 11,
    0, 13,  5, 14,  6,  8, 15,  2,
    7, 10,  8, 15,  4,  9, 11,  5,
    9,  0, 14,  3, 10,  7,  1, 12, ], [
    7, 10,  1, 15,  0, 12, 11,  5,
    14,  9,  8,  3,  9,  7,  4,  8,
    13,  6,  2,  1,  6, 11, 12,  2,
    3,  0,  5, 14, 10, 13, 15,  4,
    13,  3,  4,  9,  6, 10,  1, 12,
    11,  0,  2,  5,  0, 13, 14,  2,
    8, 15,  7,  4, 15,  1, 10,  7,
    5,  6, 12, 11,  3,  8,  9, 14, ], [
    2,  4,  8, 15,  7, 10, 13,  6,
    4,  1,  3, 12, 11,  7, 14,  0,
    12,  2,  5,  9, 10, 13,  0,  3,
    1, 11, 15,  5,  6,  8,  9, 14,
    14, 11,  5,  6,  4,  1,  3, 10,
    2, 12, 15,  0, 13,  2,  8,  5,
    11,  8,  0, 15,  7, 14,  9,  4,
    12,  7, 10,  9,  1, 13,  6,  3, ], [
    12,  9,  0,  7,  9,  2, 14,  1,
    10, 15,  3,  4,  6, 12,  5, 11,
    1, 14, 13,  0,  2,  8,  7, 13,
    15,  5,  4, 10,  8,  3, 11,  6,
    10,  4,  6, 11,  7,  9,  0,  6,
    4,  2, 13,  1,  9, 15,  3,  8,
    15,  3,  1, 14, 12,  5, 11,  0,
    2, 12, 14,  7,  5, 10,  8, 13, ], [
    4,  1,  3, 10, 15, 12,  5,  0,
    2, 11,  9,  6,  8,  7,  6,  9,
    11,  4, 12, 15,  0,  3, 10,  5,
    14, 13,  7,  8, 13, 14,  1,  2,
    13,  6, 14,  9,  4,  1,  2, 14,
    11, 13,  5,  0,  1, 10,  8,  3,
    0, 11,  3,  5,  9,  4, 15,  2,
    7,  8, 12, 15, 10,  7,  6, 12, ], [
    13,  7, 10,  0,  6,  9,  5, 15,
    8,  4,  3, 10, 11, 14, 12,  5,
    2, 11,  9,  6, 15, 12,  0,  3,
    4,  1, 14, 13,  1,  2,  7,  8,
    1,  2, 12, 15, 10,  4,  0,  3,
    13, 14,  6,  9,  7,  8,  9,  6,
    15,  1,  5, 12,  3, 10, 14,  5,
    8,  7, 11,  0,  4, 13,  2, 11, ],
]

SECRET_KEY = b'ylzsxkwm'


def bit_transform(arr_int, n, l):
    l2 = 0
    for i in range(n):
        if arr_int[i] < 0 or (l & arrayMask[arr_int[i]] == 0):
            continue
        l2 |= arrayMask[i]
    return l2


def DES64(longs, l):
    out = 0
    SOut = 0
    pR = [0] * 8
    pSource = [0, 0]
    sbi = 0
    t = 0
    L = 0
    R = 0
    out = bit_transform(arrayIP, 64, l)
    pSource[0] = 0xFFFFFFFF & out
    pSource[1] = (-4294967296 & out) >> 32
    for i in range(16):
        R = pSource[1]
        R = bit_transform(arrayE, 64, R)
        R ^= longs[i]
        for j in range(8):
            pR[j] = 255 & R >> j * 8
        SOut = 0
        for sbi in range(7, -1, -1):
            SOut <<= 4
            SOut |= matrixNSBox[sbi][pR[sbi]]

        R = bit_transform(arrayP, 32, SOut)
        L = pSource[0]
        pSource[0] = pSource[1]
        pSource[1] = L ^ R
    pSource = pSource[::-1]
    out = -4294967296 & pSource[1] << 32 | 0xFFFFFFFF & pSource[0]
    out = bit_transform(arrayIP_1, 64, out)
    return out


def sub_keys(l, longs, n):
    l2 = bit_transform(arrayPC_1, 56, l)
    for i in range(16):
        l2 = ((l2 & arrayLsMask[arrayLs[i]]) << 28 - arrayLs[i] | (l2 & ~arrayLsMask[arrayLs[i]]) >> arrayLs[i])
        longs[i] = bit_transform(arrayPC_2, 64, l2)
    j = 0
    while n == 1 and j < 8:
        l3 = longs[j]
        longs[j], longs[15-j] = longs[15-j], longs[j]
        j += 1


def encrypt(msg, key=SECRET_KEY):
    if isinstance(msg, str):
        msg = msg.encode()
    if isinstance(key, str):
        key = key.encode()
    assert (isinstance(msg, bytes))
    assert (isinstance(key, bytes))

    # 处理密钥块
    l = 0
    for i in range(8):
        l = l | key[i] << i * 8

    j = len(msg) // 8
    # arrLong1 存放的是转换后的密钥块, 在解密时只需要把这个密钥块反转就行了
    arrLong1 = [0] * 16
    sub_keys(l, arrLong1, 0)
    # arrLong2 存放的是前部分的明文
    arrLong2 = [0] * j
    for m in range(j):
        for n in range(8):
            arrLong2[m] |= msg[n + m * 8] << n * 8

    # 用于存放密文
    arrLong3 = [0] * ((1 + 8 * (j + 1)) // 8)
    # 计算前部的数据块(除了最后一部分)
    for i1 in range(j):
        arrLong3[i1] = DES64(arrLong1, arrLong2[i1])

    # 保存多出来的字节
    arrByte1 = msg[j*8:]
    l2 = 0
    for i1 in range(len(msg) % 8):
        l2 |= arrByte1[i1] << i1 * 8
    # 计算多出的那一位(最后一位)
    arrLong3[j] = DES64(arrLong1, l2)

    # 将密文转为字节型
    arrByte2 = [0] * (8 * len(arrLong3))
    i4 = 0
    for l3 in arrLong3:
        for i6 in range(8):
            arrByte2[i4] = (255 & l3 >> i6 * 8)
            i4 += 1
    return arrByte2


def base64_encrypt(msg):
    b1 = encrypt(msg)
    b2 = bytearray(b1)
    s = base64.encodebytes(b2)
    return s.replace(b'\n', b'').decode()
