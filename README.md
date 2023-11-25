<div align="center">

![lx-music-api-server-python](https://socialify.git.ci/lxmusics/lx-music-api-server-python/image?description=1&font=Inter&forks=1&issues=1&language=1&name=1&owner=1&pulls=1&stargazers=1&theme=Auto) 

![GitHub repo size](https://img.shields.io/github/repo-size/lxmusics/lx-music-api-server-python?style=for-the-badge)
![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/lxmusics/lx-music-api-server-python/build_binary.yml?style=for-the-badge)
![GitHub release (with filter)](https://img.shields.io/github/v/release/lxmusics/lx-music-api-server-python?style=for-the-badge)
![GitHub all releases](https://img.shields.io/github/downloads/lxmusics/lx-music-api-server-python/total?style=for-the-badge&color=violet)
![GitHub License](https://img.shields.io/github/license/lxmusics/lx-music-api-server-python?style=for-the-badge)

</div>

原仓库：[lx-music-api-server](https://github.com/lxmusics/lx-music-api-server)  
您可以在原仓库中找到对应的可用源脚本  


## 还在开发中
**主开发是高一住校学生，只有周末有时间回复，也欢迎所有人来贡献代码，我们在这里万分感谢**   

## 使用此项目导致的封号等情况与开发者无关

## 部署方法
环境要求：Python 3.8+  
没有其他限制，能用Python理论上就能跑起来  

测试版本部署，linux命令如果为python3请自行替换：  

```bash
git clone https://github.com/lxmusics/lx-music-api-server-python.git # clone本项目
python -m pip install -r ./requirements.txt # 安装依赖
python main.py # 启动服务
```

对于release的部署和上方类似，这里不再赘述  

## 返回码说明

接口返回值中`body.code`字段值中的代码含义

| 内容 | 含义                                 |
|------|--------------------------------------|
|  0   |成功                                  |
|  1   |IP被封禁                              |
|  2   |获取失败                              |
|  4   |服务器内部错误（对应statuscode 500）  |
|  5   |请求过于频繁                          |
|  6   |参数错误                              |

接口返回的`statuscode`对应的代码含义

| 内容 | 含义                              |
|------|-----------------------------------|
| 200  |成功                               |
| 403  |IP被封禁                           |
| 400  |参数错误                           |
| 429  |请求过于频繁                       |
| 500  |服务器内部错误（对应body.code 4）  |

## 项目协议

本项目基于 [MIT](https://github.com/lxmusics/lx-music-api-server/blob/main/LICENSE) 许可证发行，以下协议是对于MIT原协议的补充，如有冲突，以以下协议为准。

词语约定：本协议中的“本项目”指本音源项目；“使用者”指签署本协议的使用者；“官方音乐平台”指对本项目内置的包括酷我、酷狗、咪咕等音乐源的官方平台统称；“版权数据”指包括但不限于图像、音频、名字等在内的他人拥有所属版权的数据。

1. 本项目的数据来源原理是从各官方音乐平台的公开服务器中拉取数据，经过对数据简单地筛选与合并后进行展示，因此本项目不对数据的准确性负责。
2. 使用本项目的过程中可能会产生版权数据，对于这些版权数据，本项目不拥有它们的所有权，为了避免造成侵权，使用者务必在**24小时**内清除使用本项目的过程中所产生的版权数据。
3. 由于使用本项目产生的包括由于本协议或由于使用或无法使用本项目而引起的任何性质的任何直接、间接、特殊、偶然或结果性损害（包括但不限于因商誉损失、停工、计算机故障或故障引起的损害赔偿，或任何及所有其他商业损害或损失）由使用者负责。
4. 本项目完全免费，且开源发布于 GitHub 面向全世界人用作对技术的学习交流，本项目不对项目内的技术可能存在违反当地法律法规的行为作保证，**禁止在违反当地法律法规的情况下使用本项目**，对于使用者在明知或不知当地法律法规不允许的情况下使用本项目所造成的任何违法违规行为由使用者承担，本项目不承担由此造成的任何直接、间接、特殊、偶然或结果性责任。

若你使用了本项目，将代表你接受以上协议。

音乐平台不易，请尊重版权，支持正版。  
本项目仅用于对技术可行性的探索及研究，不接受任何商业（包括但不限于广告等）合作及捐赠。  
若对此有疑问请 mail to:  
helloplhm-qwq+outlook.com  
folltoshe+foxmail.com  
(请将`+`替换成`@`)

## Star 趋势图

[![Stargazers over time](https://starchart.cc/lxmusics/lx-music-api-server-python.svg)](https://starchart.cc/lxmusics/lx-music-api-server-python)

## 贡献者

<a href="https://github.com/lxmusics/lx-music-api-server-python/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=lxmusics/lx-music-api-server-python" />
</a>
