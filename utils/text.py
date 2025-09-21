import re
import ujson
from .xml import loadXML


def IsValidUTF8(text: str | bytes) -> bool:
    try:
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        if "\ufffe" in text:
            return False
        try:
            text.encode("utf-8").decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False
    except:
        return False


def IsPlainText(text: str) -> bool:
    pattern = re.compile(r"[^\x00-\x7F]")
    return not bool(pattern.search(text))


def ConvertDictToForm(dic: dict) -> str:
    return "&".join([f"{k}={v}" for k, v in dic.items()])


def LogPlainText(text: str) -> str:
    if text.startswith("{") and text.endswith("}"):
        try:
            text = ujson.loads(text)
        except:
            pass
    elif text.startswith("<xml") and text.endswith(">"):
        try:
            text = f"xml: {loadXML(text)}"
        except:
            pass
    return text


def IsChinese(check_str: str):
    for ch in check_str:
        if "\u4e00" <= ch <= "\u9fa5":
            return True
    return False
