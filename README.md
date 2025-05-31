<div align="center">

![lx-music-api-server](https://socialify.git.ci/MeoProject/lx-music-api-server/image?description=1&forks=1&issues=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2FMeoProject%2Flx-music-api-server%2Fmain%2Ficon.png&owner=1&pulls=1&stargazers=1&theme=Auto)

![GitHub Repo Size](https://img.shields.io/github/repo-size/MeoProject/lx-music-api-server?style=for-the-badge)
[![GitHub License](https://img.shields.io/github/license/MeoProject/lx-music-api-server?style=for-the-badge)](https://github.com/MeoProject/lx-music-api-server/blob/main/LICENSE)

</div>

由于使用此项目导致的**封号**等情况**与本项目无关**

本项目不接受私人定制，非**本项目 Github 发布**所出现问题**与本项目无关**

## 💡 特点

- [ ] 功能
  - [ ] 完整性 API（歌单，搜索
  - [ ] 服务器向 webdav
  - [x] 客户端播放服务器上的本地音乐
  - [x] Cookie 池
  - [x] https 监听，多端口监听
  - [x] 反代兼容性
  - [x] 获取更高的音质
  - [x] QRC 解密
- [x] 多端部署（`Windows` `Linux` `MacOS`）

## 💻 部署方法

### Release 部署（推荐）

1. 从 [Releases](https://github.com/MeoProject/lx-music-api-server/releases)
   或 [Actions](https://github.com/MeoProject/lx-music-api-server/actions)
   下载对应你系统的可执行文件 (从 GitHub Actions 下载需要登录 GitHub 账号)

2. 运行可执行文件（如果下载的文件是压缩包请先解压）

---

### Poetry 部署

环境要求: Python 3.8+

1. 安装 poetry

   ```bash
   pip install poetry
   ```

2. clone 本项目并进入项目目录

   ```bash
   git clone https://github.com/MeoProject/lx-music-api-server.git
   cd lx-music-api-server
   ```

3. 安装依赖

   ```bash
   poetry install
   ```

4. 启动

   ```bash
   poetry shell # 进入poetry环境
   python main.py # 运行项目
   ```

---

### 直接部署

环境要求：Python 3.6 - 3.11, 建议 Python 3.8+

Python 3.12 及以上会装不上依赖
没有其他限制，能用 Python 理论上就能跑起来  
linux 命令如果为 python3 请自行替换

1. clone 本项目并进入项目目录

   ```bash
   git clone https://github.com/MeoProject/lx-music-api-server.git
   cd lx-music-api-server
   ```

2. 安装依赖

   ```bash
   python -m pip install -r ./requirements.txt
   ```

3. 启动

   ```bash
   python main.py
   ```

## 📖 返回码说明

接口返回的`statuscode`和`body.code`对应的代码含义

| 内容 | 含义               |
| ---- | ------------------ |
| 200  | 成功               |
| 403  | IP 被封禁/密钥错误 |
| 400  | 参数错误           |
| 429  | 请求过于频繁       |
| 500  | 服务器内部错误     |

## 📄 项目协议

本项目基于 [MIT](https://github.com/MeoProject/lx-music-api-server/blob/main/LICENSE) 许可证发行，以下协议是对于 MIT 原协议的补充，如有冲突，以以下协议为准。

词语约定：本协议中的“本项目”指本音源项目；“使用者”指签署本协议的使用者；“官方音乐平台”指对本项目内置的包括酷我、酷狗、咪咕等音乐源的官方平台统称；“版权数据”指包括但不限于图像、音频、名字等在内的他人拥有所属版权的数据。

1. 本项目的数据来源原理是从各官方音乐平台的公开服务器中拉取数据，经过对数据简单地筛选与合并后进行展示，因此本项目不对数据的准确性负责。
2. 使用本项目的过程中可能会产生版权数据，对于这些版权数据，本项目不拥有它们的所有权，为了避免造成侵权，使用者务必在**24 小时**内清除使用本项目的过程中所产生的版权数据。
3. 由于使用本项目产生的包括由于本协议或由于使用或无法使用本项目而引起的任何性质的任何直接、间接、特殊、偶然或结果性损害（包括但不限于因商誉损失、停工、计算机故障或故障引起的损害赔偿，或任何及所有其他商业损害或损失）由使用者负责。
4. 本项目完全免费，且开源发布于 GitHub 面向全世界人用作对技术的学习交流，本项目不对项目内的技术可能存在违反当地法律法规的行为作保证，**禁止在违反当地法律法规的情况下使用本项目**，对于使用者在明知或不知当地法律法规不允许的情况下使用本项目所造成的任何违法违规行为由使用者承担，本项目不承担由此造成的任何直接、间接、特殊、偶然或结果性责任。

若你使用了本项目，将代表你接受以上协议。

音乐平台不易，请尊重版权，支持正版。  
本项目仅用于对技术可行性的探索及研究，不接受任何商业（包括但不限于广告等）合作及捐赠。  
若对此有疑问请 mail to:  
helloplhm-qwq+outlook.com  
folltoshe+foxmail.com  
(请将`+`替换成`@`)

## ✨Star 趋势图

[![Stargazers over time](https://starchart.cc/MeoProject/lx-music-api-server.svg)](https://starchart.cc/MeoProject/lx-music-api-server)

## ⚙️ 贡献者

[![Contributor](https://contrib.rocks/image?repo=MeoProject/lx-music-api-server)](https://github.com/MeoProject/lx-music-api-server/graphs/contributors)
