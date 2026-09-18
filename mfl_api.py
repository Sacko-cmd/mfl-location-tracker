from urllib.parse import urlsplit, urlunsplit

import requests

from config import MFL_API_BASE_URL, REQUEST_TIMEOUT_SECONDS

MFL_API_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Origin": "https://app.playmfl.com",
    "Referer": "https://app.playmfl.com/",
}


def normalize_mfl_url(url):
    """Upgrade known MFL endpoints, including URLs saved by old extensions."""
    parts = urlsplit(url)
    path = parts.path
    if parts.netloc == "z519wdyajg.execute-api.us-east-1.amazonaws.com" and path.startswith("/prod/"):
        path = path[len("/prod"):]
    elif parts.netloc != "api.playmfl.com":
        return url
    if parts.scheme != "https":
        return url
    base = urlsplit(MFL_API_BASE_URL)
    return urlunsplit((base.scheme, base.netloc, base.path + path, parts.query, parts.fragment))


def mfl_get(url, **kwargs):
    headers = {**MFL_API_HEADERS, **kwargs.pop("headers", {})}
    kwargs.setdefault("timeout", REQUEST_TIMEOUT_SECONDS)
    return requests.get(normalize_mfl_url(url), headers=headers, **kwargs)
