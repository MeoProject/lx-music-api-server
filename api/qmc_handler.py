from ast import Str
import httpx
from urllib.parse import urlparse
from pyqmc_rust import QMCv2Cipher
from fastapi import HTTPException, Request
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/qmc")
http = httpx.AsyncClient(verify=False, timeout=httpx.Timeout(10.0, connect=60.0))

decrypted = {
    "O4M0": "0400",
    "O8M0": "0800",
    "F0M0": "F000",
    "RSM1": "RS01",
    "Q0M0": "Q000",
    "Q0M1": "Q001",
    "AIM0": "AI00",
    "mgg": "ogg",
    "mflac": "flac",
}


def detect_content_type(url: str):
    parsed_url = urlparse(url)
    filename = parsed_url.path.split("/")[-1]
    if filename.endswith(".mgg"):
        return "audio/ogg"
    elif filename.endswith(".mflac"):
        return "audio/flac"
    else:
        return "audio/mpeg"


def get_filename(url: str):
    parsed_url = urlparse(url)
    filename = parsed_url.path.split("/")[-1]
    result = filename
    for key, value in decrypted.items():
        result = result.replace(key, value)
    return result


@router.get("/decrypt")
async def handle_decrypt_request(
    request: Request,
    url: str,
    ekey: str,
):
    try:
        cipher = QMCv2Cipher.new_from_ekey(ekey.encode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无效的密钥: {str(e)}")

    headers = {}

    range_header = request.headers.get("range")
    if range_header:
        headers["Range"] = range_header

    for header in ["if-range", "if-none-match", "if-modified-since"]:
        if value := request.headers.get(header):
            headers[header.replace("-", "_").title().replace("_", "-")] = value

    async def decrypt_stream():
        async with http.stream("GET", url, headers=headers) as response:
            offset = 0
            if range_header and response.status_code == 206:
                content_range = response.headers.get("content-range", "")
                if content_range.startswith("bytes "):
                    range_parts = content_range[6:].split("-")
                    if range_parts[0].isdigit():
                        offset = int(range_parts[0])

            async for chunk in response.aiter_bytes(chunk_size=1024 * 1024):
                if chunk:
                    data = bytearray(chunk)
                    cipher.decrypt(data, offset)
                    offset += len(chunk)
                    yield bytes(data)

    head_response = await http.head(url, headers=headers)

    content_type = detect_content_type(url)
    response_headers = {
        "Accept-Ranges": "bytes",
        "Content-Disposition": f"attachment; filename={get_filename(url)}",
        "Cache-Control": head_response.headers.get(
            "cache-control", "public, max-age=3600"
        ),
    }

    for header in ["content-length", "last-modified", "etag", "content-range"]:
        if value := head_response.headers.get(header):
            response_headers[header] = value

    return StreamingResponse(
        decrypt_stream(),
        status_code=206 if range_header else 200,
        media_type=content_type,
        headers=response_headers,
    )
