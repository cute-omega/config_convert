from typing import TypeAlias
from os.path import dirname, abspath, join
__all__ = [
    "RawSheasCealerConfig",
    "JSON5Object",
    "GITHUB_MIRRORS",
    "GITHUB_USER_CONTENT_MIRRORS",
    "skip_IPv6",
    "excluded_domains_path",
    "manual_path",
    "final_config_path",
]

# RawSheasCealerConfig is a list of tuples, where each tuple contains:
#   - list[str]: A list of domain names or patterns to match.
#   - str | None: An optional string representing a redirect target or configuration value (can be None).
#   - str: A string representing a comment, description, or additional metadata.
RawSheasCealerConfig: TypeAlias = list[tuple[list[str], str | None, str]]
JSON5Object: TypeAlias = (
    dict[str, "JSON5Object"] | list["JSON5Object"] | str | int | float | bool | None
)

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

# Flag to control whether IPv6 addresses should be skipped during network operations.
# Set to True to avoid using IPv6 (e.g., if IPv6 connectivity is unreliable or undesired).
# Set to False to allow both IPv4 and IPv6 addresses.
skip_IPv6 = True

excluded_domains_path = abspath(
    join(dirname(__file__), "..", "assets", "excluded_domains.json5")
)

manual_path = abspath(join(dirname(__file__), "..", "assets", "manual_config.json5"))

final_config_path = abspath(
    join(dirname(__file__), "..", "assets", "final_config.json")
)
