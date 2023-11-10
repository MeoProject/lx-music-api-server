# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: lxsecurity.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you know what you are doing.

from . import utils
import ujson as json
import binascii
import re

# js: path = url.replace(/^https?:\/\/[\w.:]+\//, '/')
def checklxmheader(lxm, url):
    try:
        path = url.replace(re.findall(r'(?:https?:\/\/[\w.:]+\/)', url)[0], '/').replace('//', '/')
        retvalue = re.findall(r'(?:\d\w)+', path)[0]

        cop, version = tuple(lxm.split('&'))
        version = (3 - len(version) % 3) * '0' + version
        cop = utils.inflate_raw_sync(binascii.unhexlify(cop.encode('utf-8'))).decode('utf-8')
        cop = utils.from_base64(cop).decode('utf-8')
        # print(retvalue + version)
        arr, outsideversion = tuple([cop.split(']')[0] + ']', cop.split(']')[1]])
        arr = json.loads(arr)
        version = re.findall("\\d+", version)[0]
        if (not outsideversion.startswith(version)):
            return False
        if (
        (not (version) in ("".join(arr))) and
        (not (retvalue) in "".join(arr))
        ):
            return False
        return True
    except:
        return False

exports = {
    
}