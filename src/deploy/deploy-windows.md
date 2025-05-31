---
head:
  - - meta
    - name: keywords
      content: Windows部署教程
title: Windows部署教程
icon: fas fa-file-alt
author: ikun0014
date: 2025-05-31
index: false
---

## 部署教程

1.下载并且安装 Python3.10-3.11  
前往[Python 官网](https://www.python.org/downloads/release/python-3119)下拉即可找到 Python3.11.9 的下载链接  
![图1](/images/pydown.png)  
然后安装 Python  
![图2](/images/pyinstall.png)

2.下载并且安装 Git  
[点击我加速下载](https://github.moeyy.xyz/github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe)  
![图3](/images/gitinstall.png)  
一路点击 Next 和 Install 即可

3.使用 Git 克隆仓库

```bash
git clone https://github.com/MeoProject/lx-music-api-server -b main
```

4.使用 poetry 进行依赖项安装

```bash
pip install poetry
poetry install --no-root
```

5.启动服务器

```bash
poetry run python main.py
或者 npm run start

```

如果不报错，那么恭喜您，您已经完成部署:yum:
