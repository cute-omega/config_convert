from typing import Any
from os.path import dirname, abspath, join
from json5 import load
from logging import getLogger

logger = getLogger(__name__)

__all__ = [
    "JSON5Object",
    "RawSheasCealerConfig",
    "GITHUB_MIRRORS",
    "GITHUB_USER_CONTENT_MIRRORS",
    "skip_IPv6",
    "excluded_domains_path",
    "manual_path",
    "final_config_path",
]

JSON5Object = Any | list[Any | list | bool | None] | bool | None

RawSheasCealerConfig = list[list[str], str | None, str]

GITHUB_MIRRORS = [
    "github.com",
    "ghfast.top/https://github.com",
    "xget.xi-xu.me/gh",
]

# 在重定向不可用时备用
GITHUB_USER_CONTENT_MIRRORS = [
    "raw.githubusercontent.com",
    "ghproxy.net/https://raw.githubusercontent.com",
]

skip_IPv6 = True

excluded_domains_path = abspath(
    join(dirname(__file__), "..", "assets", "excluded_domains.json5")
)

manual_path = abspath(join(dirname(__file__), "..", "assets", "manual_config.json5"))

final_config_path = abspath(
    join(dirname(__file__), "..", "assets", "final_config.json")
)
