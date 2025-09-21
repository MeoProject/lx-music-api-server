from dataclasses import dataclass


@dataclass
class UrlResponse:
    url: str
    quality: str
    ekey: str = None


@dataclass
class SongInfo:
    songId: int | str
    songName: str
    artistName: str
    albumName: str = None
    hash: str = None
    songMid: str = None
    albumId: str | int = None
    albumMid: str = None
    albumAudioId: str = None
    duration: str | int = None
    coverUrl: str = None
    contentId: str = None
    mediaMid: str = None
    lyric: dict = None


@dataclass
class Song:
    info: SongInfo
    url: UrlResponse


@dataclass
class Key:
    verify: bool
    key_valid: bool
