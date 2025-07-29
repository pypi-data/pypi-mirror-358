# code used by both js.py and css.py (and possibly tasks.py)
import hashlib
import os
import re
from functools import singledispatch
from pathlib import Path

import requests

_CACHE_DIR = ".cdn_cache"
CACHE_DIR = Path(_CACHE_DIR)

# https://stackoverflow.com/questions/70064025/regex-pattern-to-match-comments-but-not-urls
HS_COMMENT_RE = re.compile(r"(?<=[^:])(//|--).+$", re.MULTILINE)
DOUBLE_SPACE_RE = re.compile(" {2,}")


def _del_whitespace(contents: str) -> str:
    return DOUBLE_SPACE_RE.sub(" ", contents.replace("\n", " "))


def _extract_contents_cdn(url: str) -> str:
    """
    Download contents from some url
    """
    resp = requests.get(url, allow_redirects=True, verify=False, timeout=10)
    resp.raise_for_status()
    return resp.text


def cache_hash(filename: str) -> str:
    """
    Cached CDN Files are stored by the hash if its url
    """

    # sha1 will probably™ have no collsions
    return hashlib.sha1(filename.encode("UTF-8")).hexdigest()


def setup_cdn_cache() -> Path:
    CACHE_DIR.mkdir(exist_ok=True)
    gitignore = CACHE_DIR / ".gitignore"
    if not gitignore.exists():
        # .cdn_cache shan't be included in git
        gitignore.write_text("*\n")

    return CACHE_DIR


def ignore_ssl():
    """
    Ignore invalid SSL certificates (useful for local development) including warnings.
    """
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    os.environ["SSL_VERIFY"] = "0"


def extract_contents_cdn(url: str, cache=True) -> str:
    """
    Download contents from some url or from cache if possible/desired

    Args:
        url (str): online resource location
        cache (bool): use .cdn_cache if possible?
    """
    if not cache:
        return _extract_contents_cdn(url)

    cdn_cache = setup_cdn_cache()
    h_url = str(cache_hash(url))

    cache_path = cdn_cache / h_url
    if cache_path.exists():
        return extract_contents_local(str(cache_path))

    _resp = _extract_contents_cdn(url)
    cache_path.write_text(_resp)

    return _resp


def extract_contents_local(path: str | Path) -> str:
    """
    Read a file from disk
    """
    with open(path) as f:
        return f.read()


@singledispatch
def truthy(val) -> bool:
    """
    Validate if the cli argument passed is something indicating yes (e.g. 1, y, t) or simply a boolean True

    Args:
        val (bool | str):

    Returns:

    """
    raise TypeError(f"{type(val)} could not be evaluated (only str or bool)")


@truthy.register
def _(val: bool):
    """
    Usually truthy() will be used with a string
    but sometimes it can be useful to not have to do typechecking in the code,
    ergo this case
    """
    return val


@truthy.register
def _(val: None):
    """
    Usually truthy() will be used with a string
    but sometimes it can be useful to not have to do typechecking in the code,
    ergo this case
    """
    return val


@truthy.register
def _(val: str):
    """
    Useful for cli interaction with lazy people
    """
    return val.lower().startswith(("1", "t", "y"))  # true, yes etc.


@truthy.register
def _(val: int):
    """
    Negative numbers are often not truthy
    """
    return val > 0
