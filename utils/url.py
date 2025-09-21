from urllib.parse import quote, unquote, urlparse


def encodeURIComponent(component):
    if isinstance(component, str):
        component = component.encode("utf-8")
    elif not isinstance(component, bytes):
        raise TypeError("component must be str or bytes")
    return quote(component)


def decodeURIComponent(component):
    return unquote(component)


def encodeURI(uri):
    parse_result = urlparse(uri)
    params = {}
    for q in parse_result.query.split("&"):
        k, v = q.split("=")
        v = encodeURIComponent(v)
        params[k] = v
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    return parse_result._replace(query=query).geturl()


def decodeURI(uri):
    parse_result = urlparse(uri)
    params = {}
    for q in parse_result.query.split("&"):
        k, v = q.split("=")
        v = decodeURIComponent(v)
        params[k] = v
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    return parse_result._replace(query=query).geturl()
