import requests

from config import REQUEST_TIMEOUT_SECONDS

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


def mfl_get(url, **kwargs):
    headers = {**MFL_API_HEADERS, **kwargs.pop("headers", {})}
    kwargs.setdefault("timeout", REQUEST_TIMEOUT_SECONDS)
    return requests.get(url, headers=headers, **kwargs)
