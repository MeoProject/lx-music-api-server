---
head:
  - - meta
    - name: keywords
      content: Linux
title: Linux部署教程
icon: fas fa-file-alt
author: ikun0014
date: 2025-05-31
index: false
---

## Linux 部署教程，演示系统：Ubuntu 22.04

1.安装 Python,Git

```bash
sudo apt update
sudo apt install python3 python3-pip git -y
```

2.克隆仓库

```bash
git clone https://github.com/MeoProject/lx-music-api-server -b main

git clone https://github.moeyy.xyz/github.com/MeoProject/lx-music-api-server -b main
```

根据网络环境选择

3.安装依赖

```bash
pip3 install poetry
poetry install --no-root
```

4.启动服务器

```bash
poetry run python main.py
```

如果屏幕上没有报错，那么恭喜您，部署已完成!:yum:
