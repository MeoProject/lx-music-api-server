简体中文 | [English](README_EN.md)

<div align="center">

![lx-music-api-server](https://socialify.git.ci/MeoProject/lx-music-api-server/image?description=1&forks=1&issues=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2FMeoProject%2Flx-music-api-server%2Fmain%2Fres%2Ficon.png&owner=1&pulls=1&stargazers=1&theme=Auto)

![GitHub Repo Size](https://img.shields.io/github/repo-size/MeoProject/lx-music-api-server?style=for-the-badge)
[![GitHub License](https://img.shields.io/github/license/MeoProject/lx-music-api-server?style=for-the-badge)](https://github.com/MeoProject/lx-music-api-server/blob/main/LICENSE)

</div>

使用此项目导致的**封号**等情况**与本项目无关**

本项目不接受私人定制，非**本项目 Github 发布**所出现问题**与本项目无关**

PS: 主开发(@helloplhm-qwq)因学业原因无法维护项目, 在 2026 年 6 月(高考)前有事可优先联系我(@ikun0014)，同时祝主开发金榜题名，考上自己理想的大学

## 💡 功能支持性

主要功能：
- [x] 链接获取(kw,kg,tx,wy,mg)  
- [x] 详情获取(kw,kg,tx,wy,mg)  
- [x] 歌词获取(kw,kg,tx,wy,mg)  
- [x] 刷新登录(kg,tx)(只有这俩必须刷新)

- [ ] 搜索(计划外)  
- [ ] i18n(计划外)

特别功能:  
- [x] [数据已删除]加密(第二版)解密  
- [x] 歌词适配完整 API(链接获取,更新,赞助,闪屏)

## 💻 部署方法

环境要求:  
≥Python 3.10  
≥Redis 6.0  
不推荐 Red hat 系, 推荐 Debian 系和 Windows，最省事  
非必要: Node.js

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
   poetry install --no-root
   ```

4. 启动

   ```bash
   poetry run python app.py
   or
   npm run start
   ```

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
ikun+ikunshare.com  
(请将`+`替换成`@`)

## ✨Star 趋势图

[![Stargazers over time](https://starchart.cc/MeoProject/lx-music-api-server.svg)](https://starchart.cc/MeoProject/lx-music-api-server)

## ⚙️ 贡献者

[![Contributor](https://contrib.rocks/image?repo=MeoProject/lx-music-api-server)](https://github.com/MeoProject/lx-music-api-server/graphs/contributors)
