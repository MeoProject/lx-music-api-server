---
head:
  - - meta
    - name: keywords
      content: API接口
title: API接口
icon: fas fa-file-alt
author: ikun0014
date: 2025-05-31
index: false
---

# 接口列表

## 1.获取播放链接（获取会员歌曲请自行充值会员后在配置文件内填写 cookie）

| 平台          | 请求方法 | 请求路径                          |
| ------------- | -------- | --------------------------------- |
| Kuwo（kw）    | GET      | /url?source=kw&songId=m&quality=q |
| Tencent（tx） | GET      | /url?source=tx&songId=m&quality=q |
| Kugou（kg）   | GET      | /url?source=kg&songId=h&quality=q |
| Netease（wy） | GET      | /url?source=wy&songId=m&quality=q |
| Migu（mg）    | GET      | /url?source=mg&songId=m&quality=q |

参数详解：

m
: 各大平台歌曲详情页最后面的一串字符（tx 是字母+数字混合，其它都是纯数字）

h
: 酷狗音乐歌曲的哈希（hash）值，最好通过搜索接口获得

q
: 歌曲的音质，

1. 128k
2. 320k
3. flac
4. hires
5. atmos
6. atmos_plus
7. master

## 2.搜索

| 平台  | 请求方法 | 路径                           |
| ----- | -------- | ------------------------------ |
| Kugou | GET      | /search/kg/song?query=k&page=p |

参数详解：

k
: 你需要搜索的歌曲的名称

p
: 页数

## 3.MV

| 平台  | 请求方法 | 路径        |
| ----- | -------- | ----------- |
| Kugou | GET      | /mv/kg/mvid |

参数详解：

mvid
: 调用搜索接口获得

## 4.歌曲详情

| 平台    | 请求方法 | 路径       |
| ------- | -------- | ---------- |
| Kugou   | GET      | /info/kg/h |
| Tencent | GET      | /info/tx/m |

参数详解：

h
: 经典 hash 值

m
: 经典歌曲 ID
