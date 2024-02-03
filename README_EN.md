<div align="center">

![lx-music-api-server-python](https://socialify.git.ci/lxmusics/lx-music-api-server-python/image?description=1&font=Inter&forks=1&issues=1&language=1&name=1&owner=1&pulls=1&stargazers=1&theme=Auto)

![GitHub Repo Size](https://img.shields.io/github/repo-size/lxmusics/lx-music-api-server-python?style=for-the-badge)
[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/lxmusics/lx-music-api-server-python/build_beta.yml?style=for-the-badge)](https://github.com/lxmusics/lx-music-api-server-python/actions/workflows/build_beta.yml)
[![GitHub Release (with filter)](https://img.shields.io/github/v/release/lxmusics/lx-music-api-server-python?style=for-the-badge)](https://github.com/lxmusics/lx-music-api-server-python/releases/latest)
[![GitHub All Releases](https://img.shields.io/github/downloads/lxmusics/lx-music-api-server-python/total?style=for-the-badge&color=violet)](https://github.com/lxmusics/lx-music-api-server-python/releases)
[![GitHub License](https://img.shields.io/github/license/lxmusics/lx-music-api-server-python?style=for-the-badge)](https://github.com/lxmusics/lx-music-api-server/blob/main/LICENSE)

</div>

Original Repo: [lx-music-api-server](https://github.com/lxmusics/lx-music-api-server)  
You can find the corresponding available source scripts in the original repository.

**Ban** and other situations caused by the use of this project have **nothing** to do with this project.

## How to deploy

### Use Release (recommended)

1. Download the executable file corresponding to your system from [Releases](https://github.com/lxmusics/lx-music-api-server-python/releases) or [Actions](https://github.com/lxmusics/lx-music-api-server-python/actions)

2. Run the downloaded executable file (maybe you need to unzip the downloaded file if it is a compressed files)

---

### Use Poetry

Required environment: Python 3.8+

1. Install poetry

    ```bash
    pip install poetry
    ```

2. Clone this project and enter the project directory

    ```bash
    git clone https://github.com/lxmusics/lx-music-api-server-python.git
    cd lx-music-api-server-python
    ```

3. Install requirements

    ```bash
    poetry install --no-root
    ```

4. Run it

    ```bash
    poetry shell # enter poetry environment
    python main.py # run project
    ```

---

### Directly deploy

Required environment: Python 3.6 - 3.11, Python 3.8+ is better.

Python 3.12 or higher maybe install requirements failed.
Without other restrictions, you can run only with Python.
If you are using linux, you command maybe python3, please replace it yourself.

1. Clone this project and enter the project directory

    ```bash
    git clone https://github.com/lxmusics/lx-music-api-server-python.git
    cd lx-music-api-server-python
    ```

2. Install requirements

    ```bash
    python -m pip install -r ./requirements.txt
    ```

3. Run it

    ```bash
    python main.py
    ```

---

### Use Docker

Required environment: Docker

This method **has not been tested**, and we don't know the required Docker version, so you can try whether the existing Docker version can be run by yourself.

1. Update package

    ```bash
    sudo apt-get update
    ```

2. install Docker (skip if you already have it)

    ```bash
    sudo apt-get install -y docker.io
    ```

3. Create container

    ```bash
    docker run  --name lx-music-api-server-python -p 9763:9763 -d ikun0014/lx-music-api-server-python:latest
    ```

4. Get container directory

    ```bash
    docker inspect lx-music-api-server-python
    ```

5. Go to the `/app` directory in the container directory and modify `config.json`.

## Return code description

The code meaning in the `body.code` field value in the interface return value.

| Value | Meaning                                               |
| ---- | --------------------------------------------------- |
| 0    | Success                                                 |
| 1    | IP is banned or does not support anti-generation      |
| 2    | Fail to obtain.                                         |
| 4    | Server internal error (corresponding to statuscode 500) |
| 5    | Too frequent requests                                   |
| 6    | Parameter error                                        |

The code meaning of `statuscode` returned by the interface.

| Value | Meaning                                              |
| ---- | -------------------------------------------------- |
| 200  | Success                                               |
| 403  | IP is banned                                          |
| 400  | Parameter error                                      |
| 429  | Too frequent requests                                |
| 500  | Server internal error (corresponding to body.code 4) |

## Remarks

### The following excellent codes may appear in this project.

1. Triangle has stability.

    ```python
    for a in xxx:
      if (xxx):
        if (xxx):
          if (xxx):
            for b in xxx:
              if (xxx):
                while (xxx):
                  pass
                pass
              pass
            pass
          pass
        pass
      pass
    ```

2. If you can finish it in one line, then don't write many lines.

    ```python
    sys.stdout.write('\r|'+'=' * (int(dd['pares'].index(ds) / total * 50)) + ' ' * (49 - int(dd['pares'].index(ds) / total * 50)) + f'''|{int(dd['pares'].index(ds) / total * 100)}%    xx''' + ds['title']+' ' * 20)
    ```

3. Do not reuse duplicate parts

    ```python
    async def other(method, source, songid, _):
        try:
            func = require('modules.' + source + '.' + method)
        except:
            return {
                'code': 1,
                'msg': '未知的源或不支持的方法',
                'data': None,
            }
        try:
            result = await func(songid)
            return {
                'code': 0,
                'msg': 'success',
                'data': result
            }
        except FailedException as e:
            return {
                'code': 2,
                'msg': e.args[0],
                'data': None,
            }

    async def other_with_query(method, source, t, _, query):
        try:
            func = require('modules.' + source + '.' + method)
        except:
            return {
                'code': 1,
                'msg': '未知的源或不支持的方法',
                'data': None,
            }
        try:
            result = await func(t, query)
            return {
                'code': 0,
                'msg': 'success',
                'data': result
            }
        except FailedException as e:
            return {
                'code': 2,
                'msg': e.args[0],
                'data': None,
            }
    ```

4. Module does not split

    Details at [config.py](https://github.com/lxmusics/lx-music-api-server-python/tree/main/common/config.py)

5. Unknown variable name

    ```python
    a = '小明'
    b = 1
    c = 2
    d = b''
    def e(a, b, c):
      c = xxx
      d = xxx
    f = e(c, b, a)
    ```

## Project agreement

This project is issued under [MIT](https://github.com/lxmusics/lx-music-api-server/blob/main/LICENSE) license. The following agreement is a supplement to the original MIT agreement. In case of conflict, the following agreement shall prevail.

Word agreement: "this project" in this agreement refers to this audio source project; "User" means the user who signed this Agreement; "Official Music Platform" refers to the official platforms built in this project, including Cool Me, Cool Dog, Mi Gu and other music sources; "Copyright data" refers to data of which others have copyright, including but not limited to images, audio, names, etc.

1. The data source principle of this project is to pull data from the public servers of official music platforms, and display the data after simple screening and merging, so this project is not responsible for the accuracy of the data.
2. Copyright data may be generated during the use of this project, and this project does not own the copyright data. In order to avoid infringement, users must clear the copyright data generated during the use of this project within **24 hours**.
3. Any direct, indirect, special, accidental or consequential damages of any nature arising from the use of this project (including but not limited to damages caused by loss of goodwill, shutdown, computer failure or malfunction, or any and all other commercial damages or losses) shall be borne by the user.
4. This project is completely free of charge, and the open source is published on GitHub for people all over the world to learn and exchange technology. This project does not guarantee that the technology in the project may violate local laws and regulations. **It is forbidden to use this project in violation of local laws and regulations.** The user shall bear any illegal acts caused by the user knowing or not knowing that the local laws and regulations do not allow it, and this project will not bear any direct, indirect, special, accidental or consequential responsibilities.

If you use this project, you will accept the above agreement on your behalf.  
Music platform is not easy, please respect copyright and support genuine.

This project is only used for the exploration and research of technical feasibility, and does not accept any commercial (including but not limited to advertising) cooperation and donation.  
If you have any questions about this, please mail to:  
helloplhm-qwq+outlook.com  
folltoshe+foxmail.com  
(please replace `+` to `@`)

## Star trend chart

[![Stargazers over time](https://starchart.cc/lxmusics/lx-music-api-server-python.svg)](https://starchart.cc/lxmusics/lx-music-api-server-python)

## Contributor

[![Contributor](https://contrib.rocks/image?repo=lxmusics/lx-music-api-server-python)](https://github.com/lxmusics/lx-music-api-server-python/graphs/contributors)
