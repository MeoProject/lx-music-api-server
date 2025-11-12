from fastapi import Request
from fastapi.responses import ORJSONResponse


def handleResponse(request: Request, body: dict) -> ORJSONResponse:
    status = body.get("code", 200)

    if "visiter_info" not in body:
        body["visiter_info"] = {
            "ip": request.state.remote_addr,
            "ua": request.headers.get("User-Agent", ""),
        }

    return ORJSONResponse(
        body, status_code=status, headers={"Access-Control-Allow-Origin": "*"}
    )
