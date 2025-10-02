# 快速开始

环境要求:

1. Python ≥ 3.10
2. Redis ≥ 6.0

步骤:

- 1 获取项目源码并进入项目目录

```
git clone https://github.com/MeoProject/lx-music-api-server
cd lx-music-api-server
```

- 2 安装项目依赖

```
pip install poetry
poetry install --no-root
```

- 3 启动项目以生成配置文件

```
poetry run python app.py
```

- 4 配置项目

已于 3.0.0 版本为配置文件增加 JSON Schema, 使用 VSCode 等编辑器将鼠标悬停于配置键上即可获得配置简介

- 5 启动项目

```
poetry run python app.py
```
