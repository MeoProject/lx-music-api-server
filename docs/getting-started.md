# 快速开始

环境要求:

1. Python ≥ 3.10
2. Redis ≥ 6.0

步骤:

- 1 安装 uv

```
Win: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
Linux/Darwin: curl -LsSf https://astral.sh/uv/install.sh | sh
```

如果你在中国大陆，请参考 https://gitee.com/wangnov/uv-custom/releases

- 2 克隆项目并进入项目目录

```
git clone https://github.com/MeoProject/lx-music-api-server.git
cd lx-music-api-server
```

- 3 同步环境

```
uv sync
```

- 5 启动项目, 配置项目

```
uv run main.py
```
