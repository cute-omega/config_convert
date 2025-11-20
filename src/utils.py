from logging import Logger, getLogger
from ipaddress import ip_address

__all__ = [
    "is_ipv6_address",
    "show_raw_text_for_debugging",
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


def show_raw_text_for_debugging(name: str, msg: str, logger: Logger):
    logger.debug(f"{name} raw config text (truncated to 500 chars):")
    logger.debug(f"{msg[:500]}{'...(truncated)' if len(msg) > 500 else ''}")
