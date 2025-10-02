# from https://static.v2.sukimon.me:8443/DNS.py

import random
import aiohttp
import asyncio
import socket
import time
import base64
import ujson
import struct
import dns.message

from aiohttp.abc import AbstractResolver
from typing import List, Tuple, Union
from utils.log import createLogger
from server.config import config

logger = createLogger("DNS Resolver")


def build_packet_inplace(domain, query_type="A"):
    """
    构造DNS查询包

    :param domain: 要查询的域名
    :param query_type: 查询类型（默认为A记录，支持A, MX, CNAME等）
    :return: 构造的DNS查询包
    """
    # DNS报文头部
    transaction_id = 0  # 事务ID，任意选择
    flags = 0x0100  # 标志字段，标准查询
    questions = 1  # 查询的数量
    answer_rrs = 0  # 回答资源记录数
    authority_rrs = 0  # 权威资源记录数
    additional_rrs = 0  # 附加资源记录数

    # DNS请求报文头部
    header = struct.pack(
        ">HHHHHH",
        transaction_id,
        flags,
        questions,
        answer_rrs,
        authority_rrs,
        additional_rrs,
    )

    # 域名部分
    query_parts = domain.split(".")
    query = b"".join(
        [struct.pack("B", len(part)) + part.encode() for part in query_parts]
    )
    query = query + b"\0"  # 域名结束符

    # 查询类型和查询类映射
    query_types = {
        "A": 1,  # A记录
        "MX": 15,  # MX记录
        "CNAME": 5,  # CNAME记录
        "NS": 2,  # NS记录
        "TXT": 16,  # TXT记录
        "AAAA": 28,  # AAAA记录
    }

    # 获取查询类型的对应值
    if query_type not in query_types:
        raise ValueError(f"Unsupported query type: {query_type}")
    query_type_code = query_types[query_type]

    query_class = 1  # IN类（Internet）

    # 合并头部和查询部分
    query_packet = header + query + struct.pack(">HH", query_type_code, query_class)

    return base64.urlsafe_b64encode(query_packet).decode("utf-8").replace("=", "")


class DNSException(Exception):
    def __init__(self, host: str, error_message: str):
        self.host = host
        self.error_message = error_message
        self.print_message = f"Error resolving {self.host}: {self.error_message}"
        super().__init__(self.print_message)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.print_message}"


class DNSResolver:
    def __init__(self, ipv6_enable: bool = None, cache_ttl: int = 600):
        """
        初始化 DNSResolver 类。
        :param ipv6_enable: 是否启用 IPv6，如果为 None，则自动检测。
        :param cache_ttl: 缓存时长，单位为秒（默认 600 秒）。
        """
        self.doh = (
            config.read("module.doh")
            if len(config.read("module.doh")) != 0
            else ["https://dns.alidns.com/dns-query"]
        )
        self.ipv6_enable = (
            ipv6_enable if ipv6_enable is not None else self._check_ipv6_support()
        )
        self.cache_ttl = cache_ttl
        self.session = aiohttp.ClientSession()
        self.cache = {}

    def _check_ipv6_support(self) -> bool:
        """检查本机是否支持 IPv6。"""
        try:
            socket.create_connection(("2606:4700:4700::1111", 53), timeout=5)
            return True
        except (OSError, socket.timeout):
            return False

    async def resolve(
        self,
        host: str,
        records: Union[List[str], Tuple[str], str] = None,
    ) -> List[dict]:
        """
        解析域名。
        :param host: 要解析的主机名。
        :param records: 查询的记录类型，例如 ["A", "AAAA", "MX"]。
                        如果为 None，则根据 IPv6 支持情况自动设置。
        :return: 包含解析结果的列表。
        """
        if records is None:
            records = ["AAAA", "A"] if self.ipv6_enable else ["A"]
        if isinstance(records, str):
            records = [records]

        logger.debug(f"Try resolving: {host} record_type={records}")

        tasks = [self._resolve_with_cache(host, record) for record in records]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        final_results = []
        for result in results:
            if isinstance(result, DNSException):
                logger.warning(str(result))
            elif isinstance(result, Exception):
                logger.warning(f"Unexpected error: {result}")
            else:
                final_results.extend(result)

        logger.debug(
            f"Resolve finished: {host} record_type={records} complete -> {final_results}"
        )
        if not final_results:
            raise DNSException(host, "DNS_PROBE_FINISHED_NXDOMAIN")
        return final_results

    async def _resolve_with_cache(self, host: str, record_type: str) -> List[dict]:
        """
        带缓存的解析方法。
        :param host: 要解析的主机名。
        :param record_type: 查询的记录类型。
        :return: 包含解析结果的列表。
        """
        cache_key = (host, record_type)
        current_time = time.time()
        if cache_key in self.cache:
            timestamp, data = self.cache[cache_key]
            if current_time - timestamp < self.cache_ttl and data is not None:
                logger.debug("cache hit!")
                return data

        result = await self._resolve(host, record_type)
        self.cache[cache_key] = (current_time, result)
        return result

    async def _resolve(self, host: str, record_type: str) -> List[dict]:
        """
        通用解析方法，支持 JSON 或 DNS 数据包格式的响应。
        :param host: 要解析的主机名。
        :param record_type: 查询的记录类型，例如 "A" 或 "AAAA"。
        :return: 包含解析结果的列表。
        """
        headers = {"Accept": "application/dns-json"}
        params = {
            "name": host,
            "type": record_type,
            "dns": build_packet_inplace(host, record_type),
        }
        logger.debug(f"send >> {params}")

        try:
            response = await self.session.get(
                str(random.choice(self.doh)), headers=headers, params=params
            )
            content = await response.content.read()
            logger.debug(f"recv << {content}")

            if response.status == 200:
                # 判断响应类型
                if response.content_type.endswith("json"):
                    # 如果是 JSON 格式，使用 JSON 解析
                    try:
                        data = ujson.loads(content.decode("utf-8"))
                        return data.get("Answer", [])
                    except ujson.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        raise DNSException(host, f"{record_type}: JSON_PARSE_ERROR")
                else:
                    # 如果是 DNS 数据包格式，使用 dnspython 解析
                    try:
                        dns_message = dns.message.from_wire(content)
                        return self._parse_dns_message(dns_message)
                    except dns.exception.DNSException as e:
                        logger.error(f"DNS decode error: {e}")
                        raise DNSException(host, f"{record_type}: DNS_PARSE_ERROR")
            else:
                raise DNSException(
                    host, f"{record_type}: STATUS_NOT_SUCCESS({response.status})"
                )
        except Exception as e:
            if not isinstance(e, DNSException):
                raise DNSException(host, f"{record_type}: INTERNAL_ERROR({str(e)})")
            else:
                raise e from None

    def _parse_dns_message(self, dns_message: dns.message.Message) -> List[dict]:
        """
        解析 DNS 消息中的答复部分。
        :param dns_message: dnspython 解析后的 DNS 消息对象。
        :return: 解析得到的答案列表。
        """
        answers = []
        for answer in dns_message.answer:
            # logger.debug()
            ans = list(answer.items.keys())
            if ans:
                record = {
                    "name": answer.name.to_text(),
                    "type": dns.rdatatype.to_text(answer.rdtype),
                    "ttl": answer.ttl,
                    "data": str(ans[0]).split(" ")[-1],
                }
                answers.append(record)
        return answers

    async def close(self):
        """关闭 aiohttp 客户端会话。"""
        await self.session.close()


class aiohttpResolver(AbstractResolver):
    def __init__(self, dns_resolver: DNSResolver):
        self.dns_resolver = dns_resolver

    async def resolve(
        self, host: str, port: int = 0, family: int = socket.AF_UNSPEC
    ) -> List[Tuple]:
        """
        解析域名并返回 aiohttp规范的Host 列表。
        :param host: 要解析的主机名。
        :param port: 端口号。
        :param family: 地址族 (AF_INET, AF_INET6, 或 AF_UNSPEC)。
        :return: Host 对象列表。
        """
        record_types = []
        if family in (socket.AF_INET, socket.AF_UNSPEC):
            record_types.append("A")
        if family in (socket.AF_INET6, socket.AF_UNSPEC):
            record_types.append("AAAA")

        answers = await self.dns_resolver.resolve(host, records=record_types)

        result = []
        for answer in answers:
            if "data" in answer:
                ip_address = answer["data"]
                # 根据 IP 类型决定家庭 (AF_INET 或 AF_INET6)
                family_type = socket.AF_INET6 if ":" in ip_address else socket.AF_INET
                result.append(
                    {"host": answer["data"], "family_type": family_type, "port": port}
                )

        return result

    async def close(self):
        """关闭 DNSResolver 会话。"""
        await self.dns_resolver.close()
