import re
import ujson
from fastapi import APIRouter, Request, Response
from server.config import config
from utils.response import handleResponse
from utils.md5 import createMD5

router = APIRouter()


@router.get("/script")
async def lx_script(request: Request, key: str | None = None):
    try:
        with open(f"./static/lx-source.js", "r", encoding="utf-8") as f:
            script = f.read()
    except:
        return handleResponse(request, {"code": 404, "message": "本地无源脚本"})

    scriptLines = script.split("\n")
    newScriptLines = []

    for line in scriptLines:
        oline = line
        line = line.strip()
        url = f"{request.state.proto}://{request.state.host}{':' + str(request.url.port) if request.url.port else ''}"
        if line.startswith("const API_URL"):
            newScriptLines.append(f'''const API_URL = "{url}"''')
        elif line.startswith("const API_KEY"):
            newScriptLines.append(f'''const API_KEY = "{key if key else ''}"''')
        elif line.startswith("* @name"):
            newScriptLines.append(" * @name " + config.read("script.name"))
        elif line.startswith("* @description"):
            newScriptLines.append(" * @description " + config.read("script.intro"))
        elif line.startswith("* @author"):
            newScriptLines.append(" * @author ikunshare")
        elif line.startswith("* @version"):
            newScriptLines.append(" * @version " + config.read("script.version"))
        elif line.startswith("const DEV_ENABLE "):
            newScriptLines.append(
                "const DEV_ENABLE = " + str(config.read("script.dev")).lower()
            )
        elif line.startswith("const UPDATE_ENABLE "):
            newScriptLines.append(
                "const UPDATE_ENABLE = " + str(config.read("script.update")).lower()
            )
        else:
            newScriptLines.append(oline)

    r = "\n".join(newScriptLines)

    r = re.sub(
        r"const MUSIC_QUALITY = {[^}]+}",
        f"const MUSIC_QUALITY = JSON.parse('{ujson.dumps(config.read('script.qualitys'))}')",
        r,
    )

    if config.read("script.update"):
        md5 = createMD5(r)
        r = r.replace(r'const SCRIPT_MD5 = "";', f'const SCRIPT_MD5 = "{md5}";')
        if request.query_params.get("checkUpdate"):
            if request.query_params.get("checkUpdate") == md5:
                return handleResponse(request, {"code": 200, "message": "成功"})
            url = f"{request.state.proto}://{request.state.host}{':' + str(request.url.port) if request.url.port else ''}"
            updateUrl = f"{url}/script{('?key=' + key) if key else ''}"
            updateMsg = (
                str(config.read("script.updateMsg"))
                .format(
                    updateUrl=updateUrl,
                    url=url,
                    key=key,
                    version=config.read("script.version"),
                )
                .replace("\\n", "\n")
            )
            return handleResponse(
                request,
                {
                    "code": 200,
                    "message": "成功",
                    "data": {"updateMsg": updateMsg, "updateUrl": updateUrl},
                },
            )

    return Response(
        content=r,
        media_type="text/javascript",
        headers={
            "Content-Disposition": f"""attachment; filename={(
                config.read('script.file') 
                if config.read('script.file').endswith('.js') 
                else config.read('script.file') + '.js'
            )}"""
        },
    )
