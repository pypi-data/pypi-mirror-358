import requests
from urllib.parse import quote

PROXY_BASE = "https://proxy.montgomerynx.com"
API_KEY = None  # Set with set_api_key("your_key")


def set_api_key(key: str):
    """Set the global API key used for all proxied requests."""
    global API_KEY
    API_KEY = key


def _proxify_url(url: str) -> str:
    """Rewrite the URL to go through the proxy."""
    if not API_KEY:
        raise ValueError("API key not set. Call set_api_key('your_key') first.")
    return f"{PROXY_BASE}/{API_KEY}/{quote(url, safe='')}"


# Re-export everything else transparently
__all__ = [
    "get", "post", "put", "delete", "head", "options",
    "set_api_key"
]

# Main passthroughs
def get(url, *args, **kwargs):
    return requests.get(_proxify_url(url), *args, **kwargs)

def post(url, *args, **kwargs):
    return requests.post(_proxify_url(url), *args, **kwargs)

def put(url, *args, **kwargs):
    return requests.put(_proxify_url(url), *args, **kwargs)

def delete(url, *args, **kwargs):
    return requests.delete(_proxify_url(url), *args, **kwargs)

def head(url, *args, **kwargs):
    return requests.head(_proxify_url(url), *args, **kwargs)

def options(url, *args, **kwargs):
    return requests.options(_proxify_url(url), *args, **kwargs)
