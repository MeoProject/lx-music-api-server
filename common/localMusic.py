# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: localMusic.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

import platform
import subprocess
import sys
from PIL import Image
import aiohttp
from common.utils import createFileMD5, createMD5, timeLengthFormat
from . import log, config
import ujson as json
import traceback
import mutagen
import os

logger = log.log('local_music_handler')

audios = []
map = {}
AUDIO_PATH = config.read_config("common.local_music.audio_path")
TEMP_PATH = config.read_config("common.local_music.temp_path")
FFMPEG_PATH = None

def convertCover(input_bytes):
    if (input_bytes.startswith(b'\xff\xd8\xff\xe0')): # jpg object do not need convert
        return input_bytes
    temp = TEMP_PATH + '/' + createMD5(input_bytes) + '.img'
    with open(temp, 'wb') as f:
        f.write(input_bytes)
        f.close()
    img = Image.open(temp)
    img = img.convert('RGB')
    with open(temp + 'crt', 'wb') as f:
        img.save(f, format='JPEG')
        f.close()
    data = None
    with open(temp + 'crt', 'rb') as f:
        data = f.read()
        f.close()
    try:
        os.remove(temp)
    except:
        pass
    try:
        os.remove(temp + 'crt')
    except:
        pass
    return data

def check_ffmpeg():
    logger.info('正在检查ffmpeg')
    devnull = open(os.devnull, 'w')
    linux_bin_path = '/usr/bin/ffmpeg'
    environ_ffpmeg_path = os.environ.get('FFMPEG_PATH')
    if (platform.system() == 'Windows' or platform.system() == 'Cygwin'):
        if (environ_ffpmeg_path and (not environ_ffpmeg_path.endswith('.exe'))):
            environ_ffpmeg_path += '/ffmpeg.exe'
    else:
        if (environ_ffpmeg_path and os.path.isdir(environ_ffpmeg_path)):
            environ_ffpmeg_path += '/ffmpeg'

    if (environ_ffpmeg_path):
        try:
            subprocess.Popen([environ_ffpmeg_path, '-version'], stdout=devnull, stderr=devnull)
            devnull.close()
            return environ_ffpmeg_path
        except:
            pass

    if (os.path.isfile(linux_bin_path)):
        try:
            subprocess.Popen([linux_bin_path, '-version'], stdout=devnull, stderr=devnull)
            devnull.close()
            return linux_bin_path
        except:
            pass

    try: 
        subprocess.Popen(['ffmpeg', '-version'], stdout=devnull, stderr=devnull)
        return 'ffmpeg'
    except:
        logger.warning('无法找到ffmpeg，对于本地音乐的一些扩展功能无法使用，如果您不需要，请忽略本条提示')
        logger.warning('如果您已经安装，请将 FFMPEG_PATH 环境变量设置为您的ffmpeg安装路径或者将其添加到PATH中')
        return None

def getAudioCoverFromFFMpeg(path):
    if (not FFMPEG_PATH):
        return None
    cmd = [FFMPEG_PATH, '-i', path, TEMP_PATH + '/_tmp.jpg']
    popen = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stdout)
    popen.wait()
    if (os.path.exists(TEMP_PATH + '/_tmp.jpg')):
        with open(TEMP_PATH + '/_tmp.jpg', 'rb') as f:
            data = f.read()
            f.close()
        try:
            os.remove(TEMP_PATH + '/_tmp.jpg')
        except:
            pass
        return data

def readFileCheckCover(path):
    with open(path, 'rb') as f: # read the first 1MB audio
        data = f.read(1024 * 1024)
        return b'image/' in data

def checkLyricValid(lyric_content):
    if (lyric_content is None):
        return False
    if (lyric_content == ''):
        return False
    lines = lyric_content.split('\n')
    for line in lines:
        line = line.strip()
        if (line == ''):
            continue
        if (line.startswith('[')):
            continue
        if (not line.startswith('[')):
            return False
    return True

def filterLyricLine(lyric_content: str) -> str:
    lines = lyric_content.split('\n')
    completed = []
    for line in lines:
        line = line.strip()
        if (line.startswith('[')):
            completed.append(line)
        continue
    return '\n'.join(completed)

def getAudioMeta(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        audio = mutagen.File(filepath)
        if not audio:
            return None
        logger.debug(audio.items())
        if (filepath.lower().endswith('.mp3')):
            cover = audio.get('APIC:')
            if (cover):
                cover = convertCover(cover.data)
            
            title = audio.get('TIT2')
            artist = audio.get('TPE1')
            album = audio.get('TALB')
            lyric = audio.get('TLRC')
            if (title):
                title = title.text
            if (artist):
                artist = artist.text
            if (album):
                album = album.text
            if (lyric):
                lyric = lyric.text
            if (not lyric):
                if (os.path.isfile(os.path.splitext(filepath)[0] + '.lrc')):
                    with open(os.path.splitext(filepath)[0] + '.lrc', 'r', encoding='utf-8') as f:
                        t = f.read().replace('\ufeff', '')
                        logger.debug(t)
                        lyric = filterLyricLine(t)
                        logger.debug(lyric)
                        if (not checkLyricValid(lyric)):
                            lyric = [None]
                        else:
                            lyric = [lyric]
                        f.close()
                else:
                    lyric = [None]
        else:
            cover = audio.get('cover')
            if (cover):
                cover = convertCover(cover[0])
            else:
                if (readFileCheckCover(filepath)):
                    cover = getAudioCoverFromFFMpeg(filepath)
                else:
                    cover = None
            title = audio.get('title')
            artist = audio.get('artist')
            album = audio.get('album')
            lyric = audio.get('lyrics')
            if (not lyric):
                if (os.path.isfile(os.path.splitext(filepath)[0] + '.lrc')):
                    with open(os.path.splitext(filepath)[0] + '.lrc', 'r', encoding='utf-8') as f:
                        lyric = filterLyricLine(f.read())
                        if (not checkLyricValid(lyric)):
                            lyric = [None]
                        else:
                            lyric = [lyric]
                        f.close()
                else:
                    lyric = [None]
        return {
            "filepath": filepath,
            "title": title[0] if title else '',
            "artist": '、'.join(artist) if artist else '',
            "album": album[0] if album else '',
            "cover_path": extractCover({
                "filepath": filepath,
                "cover": cover,
            }, TEMP_PATH),
            "lyrics": lyric[0],
            'length': audio.info.length,
            'format_length': timeLengthFormat(audio.info.length),
            'md5': createFileMD5(filepath),
        }
    except:
        logger.error(f"get audio meta error: {filepath}")
        logger.error(traceback.format_exc())
        return None

def checkAudioValid(path):
    if not os.path.exists(path):
        return False
    try:
        audio = mutagen.File(path)
        if not audio:
            return False
        return True
    except:
        logger.error(f"check audio valid error: {path}")
        logger.error(traceback.format_exc())
        return False

def extractCover(audio_info, temp_path):
    if (not audio_info['cover']):
        return None
    path = os.path.join(temp_path + '/' + createMD5(audio_info['filepath']) + '_cover.jpg')
    with open(path, 'wb') as f:
        f.write(audio_info['cover'])
    return path

def findAudios(cache):

    available_exts = [
        'mp3',
        'wav',
        'flac',
        'ogg',
        'm4a',
    ]
    
    files = os.listdir(AUDIO_PATH)
    if (files == []): 
        return []
    
    audios = []
    _map = {}
    for c in cache:
        _map[c['filepath']] = c
    for file in files:
        if (not file.endswith(tuple(available_exts))):
            continue
        path = os.path.join(AUDIO_PATH, file)
        if (not checkAudioValid(path)):
            continue
        logger.info(f"found audio: {path}")
        if (not (_map.get(path) and _map[path]['md5'] == createFileMD5(path))):
            meta = getAudioMeta(path)
            audios = audios + [meta]
        else:
            audios = audios + [_map[path]]
    
    return audios

def getAudioCover(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        audio = mutagen.File(filepath)
        if not audio:
            return None
        return convertCover(audio.get('APIC:').data)
    except:
        logger.error(f"get audio cover error: {filepath}")
        logger.error(traceback.format_exc())
        return None

def writeAudioCover(filepath):
    s = getAudioCover(filepath)
    path = os.path.join(TEMP_PATH + '/' + createMD5(filepath) + '_cover.jpg')
    with open(path, 'wb') as f:
        f.write(s)
        f.close()
    return path

def writeLocalCache(audios):
    with open(TEMP_PATH + '/meta.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps({
            "file_list": os.listdir(AUDIO_PATH),
            "audios": audios
        }, ensure_ascii = False, indent = 2))
        f.close()

def dumpLocalCache():
    try:
        TEMP_PATH = config.read_config("common.local_music.temp_path")
        with open(TEMP_PATH + '/meta.json', 'r', encoding='utf-8') as f:
            d = json.loads(f.read())
        return d
    except:
        return {
            "file_list": [],
            "audios": []
        }

def initMain():
    global FFMPEG_PATH
    FFMPEG_PATH = check_ffmpeg()
    logger.debug('找到的ffmpeg命令: ' + str(FFMPEG_PATH))
    if (not os.path.exists(AUDIO_PATH)):
        os.mkdir(AUDIO_PATH)
        logger.info(f"创建本地音乐文件夹 {AUDIO_PATH}")
    if (not os.path.exists(TEMP_PATH)):
        os.mkdir(TEMP_PATH)
        logger.info(f"创建本地音乐临时文件夹 {TEMP_PATH}")
    global audios
    cache = dumpLocalCache()
    if (cache['file_list'] == os.listdir(AUDIO_PATH)):
        audios = cache['audios']
    else:
        audios = findAudios(cache['audios'])
        writeLocalCache(audios)
    for a in audios:
        map[a['filepath']] = a
    logger.info("初始化本地音乐成功")
    logger.debug(f'本地音乐列表: {audios}')
    logger.debug(f'本地音乐map: {map}')

async def generateAudioFileResonse(path):
    try:
        w = map[path]
        return aiohttp.web.FileResponse(w['filepath'])
    except:
        return {
            'code': 2,
            'msg': '未找到文件',
            'data': None
        }, 404

async def generateAudioCoverResonse(path):
    try:
        w = map[path]
        if (not os.path.exists(w['cover_path'])):
            p = writeAudioCover(w['filepath'])
            logger.debug(f"生成音乐封面文件 {w['cover_path']} 成功")
            return aiohttp.web.FileResponse(p)
        return aiohttp.web.FileResponse(w['cover_path'])
    except:
        logger.debug(traceback.format_exc())
        return {
            'code': 2,
            'msg': '未找到封面',
            'data': None
        }, 404

async def generateAudioLyricResponse(path):
    try:
        w = map[path]
        return w['lyrics']
    except:
        return {
            'code': 2,
            'msg': '未找到歌词',
            'data': None
        }, 404

def checkLocalMusic(path):
    return {
        'file': os.path.exists(path),
        'cover': os.path.exists(map[path]['cover_path']),
        'lyric': bool(map[path]['lyrics'])
    }