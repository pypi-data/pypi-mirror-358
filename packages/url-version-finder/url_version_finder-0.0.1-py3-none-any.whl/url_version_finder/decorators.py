import re


def with_version(func):
    def wrapper(request, *args, **kwargs):
        version = _find_version(request, *args, **kwargs)
        return func(request,version, *args, **kwargs)
    return wrapper


def _find_version(request, *args, **kwargs):
    url = _get_url(request)

    if url is None:
        return None

    parts = url.split("/")

    for part in parts:
        if re.fullmatch(r"v?\d+(\.\d+)*", part):
            return part
    return None


def _get_url(request):
    if isinstance(request, dict):
        return request.get("url") or request.get("path")
    if hasattr(request, "uri"):
        return request.uri
    if hasattr(request, "path"):
        return request.path
    if hasattr(request, "url"):
        return request.url
    return None