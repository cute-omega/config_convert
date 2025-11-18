from ipaddress import ip_address
from venv import logger
from DevSidecarConfig import DevSidecarConfig
from json import loads
from logging import getLogger

logger = getLogger(__name__)


__all__ = [
    "GITHUB_MIRRORS",
    "GITHUB_USER_CONTENT_MIRRORS",
    "is_ipv6_address",
    "convert_sc_config",
]


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


def is_ipv6_address(target: str) -> bool:
    # 处理形如 [240e::] 的格式
    if target.startswith("[") and target.endswith("]"):
        addr = target.strip("[]")
        try:
            return ip_address(addr).version == 6
        except ValueError:
            return False
    return False


def convert_sc_config(
    sc_config_text: str, ExcludedDomains: list[str]
) -> DevSidecarConfig:
    try:
        sc_config: list[tuple[list[str], str | None, str]] = loads(sc_config_text)
        logger.info(f"Loaded Sheas Cealer config with {len(sc_config)} items")
    except Exception as e:
        logger.error(
            f"Failed to load Sheas Cealer config: {e}\nRaw Text:\n{sc_config_text}"
        )
        raise

    ds_config = DevSidecarConfig({"server": {"intercepts": {}, "preSetIpList": {}}})

    for item in sc_config:
        sni: str | None = item[1]
        if sni is None:
            continue
        elif sni == "":
            sni = "none"

        target: str = item[2]
        if target == "":
            target = "127.0.0.1"

        skip_IPv6 = is_ipv6_address(target)

        raw_domains: list[str] = item[0]
        domains = [
            domain
            for raw_domain in raw_domains
            if raw_domain.find("^") == -1
            and ((domain := raw_domain.lstrip("$#")) not in ExcludedDomains)
        ]
        domain_rules = "|".join(domains)
        if len(domains) > 1:
            domain_rules = f"({domain_rules})"

        if domain_rules:
            ds_config["server"].setdefault("intercepts", {}).setdefault(
                domain_rules, {}
            ).setdefault(".*", {})["sni"] = sni

            if not skip_IPv6:
                ds_config["server"].setdefault("preSetIpList", {}).setdefault(
                    domain_rules, {}
                )[target] = True

    return ds_config
