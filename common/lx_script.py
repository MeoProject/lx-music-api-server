# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: lx.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from . import Httpx
from . import config
from . import scheduler
from .log import log
from aiohttp.web import Response
import ujson as json
import re
from common.utils import createMD5

logger = log('lx_script')

jsd_mirror_list = [
    'https://cdn.jsdelivr.net',
    'https://gcore.jsdelivr.net',
    'https://fastly.jsdelivr.net',
    'https://jsd.cdn.zzko.cn',
    'https://jsdelivr.b-cdn.net',
]
github_raw_mirror_list = [
    'https://raw.githubusercontent.com',
    'https://mirror.ghproxy.com/https://raw.githubusercontent.com',
    'https://ghraw.gkcoll.xyz',
    'https://raw.fgit.mxtrans.net',
    'https://github.moeyy.xyz/https://raw.githubusercontent.com',
    'https://raw.fgit.cf',
]

async def get_response(retry = 0):
    if (retry > 21):
        logger.warning('请求源脚本内容失败')
        return
    baseurl = '/MeoProject/lx-music-api-server/main/lx-music-source-example.js'
    jsdbaseurl = '/gh/MeoProject/lx-music-api-server@main/lx-music-source-example.js'
    try:
        i = retry
        if (i > 10):
            i = i - 11
        if (i < 5):
            req = await Httpx.AsyncRequest(jsd_mirror_list[retry] + jsdbaseurl)
        elif (i < 11):
            req = await Httpx.AsyncRequest(github_raw_mirror_list[retry - 5] + baseurl)
        if (not req.text.startswith('/*!')):
            logger.info('疑似请求到了无效的内容，忽略')
            raise Exception from None
    except Exception as e:
        if (isinstance(e, RuntimeError)):
            if ('Session is closed' in str(e)):
                logger.error('脚本更新失败，clientSession已被关闭')
                return
        return await get_response(retry + 1)
    return req
async def get_script():
    req = await get_response()
    if (req.status == 200):
        with open('./lx-music-source-example.js', 'w', encoding='utf-8') as f:
            f.write(req.text)
            f.close()
        logger.info('更新源脚本成功')
    else:
        logger.warning('请求源脚本内容失败')

async def generate_script_response(request):
    if (request.query.get('key') not in config.read_config('security.key.values') and config.read_config('security.key.enable')):
        return {'code': 6, 'msg': 'key验证失败', 'data': None}, 403
    try:
        with open('./lx-music-source-example.js', 'r', encoding='utf-8') as f:
            script = f.read()
    except:
        return {'code': 4, 'msg': '本地无源脚本', 'data': None}, 400
    scriptLines = script.split('\n')
    newScriptLines = []
    for line in scriptLines:
        oline = line
        line = line.strip()
        if (line.startswith('const API_URL')):
            newScriptLines.append(f'''const API_URL = "{'https' if config.read_config('common.ssl_info.is_https') else 'http'}://{request.host}"''')
        elif (line.startswith('const API_KEY')):
            newScriptLines.append(f"""const API_KEY = `{request.query.get("key") if request.query.get("key") else ''''''}`""")
        elif (line.startswith("* @name")):
            newScriptLines.append(" * @name " + config.read_config("common.download_config.name"))
        elif (line.startswith("* @description")):
            newScriptLines.append(" * @description " + config.read_config("common.download_config.intro"))
        elif (line.startswith("* @author")):
            newScriptLines.append(" * @author " + config.read_config("common.download_config.author"))
        elif (line.startswith("* @version")):
            newScriptLines.append(" * @version " + config.read_config("common.download_config.version"))
        elif (line.startswith("const DEV_ENABLE ")):
            newScriptLines.append("const DEV_ENABLE = " + str(config.read_config("common.download_config.dev")).lower())
        elif (line.startswith("const UPDATE_ENABLE ")):
            newScriptLines.append("const UPDATE_ENABLE = " + str(config.read_config("common.download_config.update")).lower())
        else:
            newScriptLines.append(oline)
    r = '\n'.join(newScriptLines)
    
    r = re.sub(r'const MUSIC_QUALITY = {[^}]+}', f'const MUSIC_QUALITY = JSON.parse(\'{json.dumps(config.read_config("common.download_config.quality"))}\')', r)
    
    # 用于检查更新
    if (config.read_config("common.download_config.update")):
        md5 = createMD5(r)
        r = r.replace(r"const SCRIPT_MD5 = ''", f"const SCRIPT_MD5 = '{md5}'")
        if (request.query.get('checkUpdate')):
            if (request.query.get('checkUpdate') == md5):
                return {'code': 0, 'msg': 'success', 'data': None}, 200
            url = f"{'https' if config.read_config('common.ssl_info.is_https') else 'http'}://{request.host}/script"
            updateUrl = f"{url}{('?key=' + request.query.get('key')) if request.query.get('key') else ''}"
            updateMsg = config.read_config('common.download_config.updateMsg').format(updateUrl = updateUrl, url = url, key = request.query.get('key')).replace('\\n', '\n')
            return {'code': 0, 'msg': 'success', 'data': {'updateMsg': updateMsg, 'updateUrl': updateUrl}}, 200
    
    return Response(text = r, content_type = 'text/javascript',
                    headers = {
                        'Content-Disposition': f'''attachment; filename={
                            config.read_config("common.download_config.filename")
                            if config.read_config("common.download_config.filename").endswith(".js")
                            else (config.read_config("common.download_config.filename") + ".js")}'''
                    })

if (config.read_config('common.allow_download_script')):
    scheduler.append('update_script', get_script)
