from typing import Any, Dict, Protocol
import orjson


class SupportsRead(Protocol):
    def read(self, length: int = -1) -> bytes | str: ...


class SupportsWrite(Protocol):
    def write(self, s: str) -> int: ...


class JSONDecodeError(ValueError):
    pass


def loads(s: str | bytes | bytearray) -> Dict:
    """解析 JSON 字符串为字典"""
    try:
        return orjson.loads(s)
    except orjson.JSONDecodeError as e:
        raise JSONDecodeError(f"JSON 解析错误: {e}")


def load(fp: SupportsRead) -> Dict:
    """从文件对象读取并解析 JSON"""
    try:
        content = fp.read()
        return loads(content)
    except orjson.JSONDecodeError as e:
        raise JSONDecodeError(f"JSON 解析错误: {e}")


def dumps(
    obj: Any,
    *,
    indent_2: bool = False,
    serialize_np: bool = False,
    serialize_uuid: bool = False,
    serialize_dataclass: bool = False,
) -> str:
    """将对象序列化为 JSON 字符串"""
    try:
        options = 0
        if indent_2:
            options |= orjson.OPT_INDENT_2
        if serialize_np:
            options |= orjson.OPT_SERIALIZE_NUMPY
        if serialize_uuid:
            options |= orjson.OPT_SERIALIZE_UUID
        if serialize_dataclass:
            options |= orjson.OPT_SERIALIZE_DATACLASS

        result = orjson.dumps(obj, option=options) if options else orjson.dumps(obj)
        return result.decode()
    except (orjson.JSONEncodeError, TypeError) as e:
        raise ValueError(f"JSON 序列化错误: {e}")


def dump(
    obj: Any,
    fp: SupportsWrite,
    *,
    indent_2: bool = True,
    serialize_np: bool = False,
    serialize_uuid: bool = False,
    serialize_dataclass: bool = False,
) -> None:
    """将对象序列化为 JSON 并写入文件对象"""
    json_str = dumps(
        obj,
        indent_2=indent_2,
        serialize_np=serialize_np,
        serialize_uuid=serialize_uuid,
        serialize_dataclass=serialize_dataclass,
    )
    fp.write(json_str)
