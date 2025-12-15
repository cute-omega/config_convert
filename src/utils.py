from logging import Logger, getLogger
from ipaddress import ip_address

__all__ = [
    "is_ipv6_address",
    "show_raw_text_for_debugging",
    "sort_json_object",
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


def sort_json_object(obj):
    """Recursively sort mapping keys by length (desc) then alphabetically (asc)."""

    if isinstance(obj, dict):
        def sort_key(item):
            k = item[0]
            k_str = k if isinstance(k, str) else str(k)
            return (-len(k_str), k_str)

        sorted_items = sorted(obj.items(), key=sort_key)
        return {k: sort_json_object(v) for k, v in sorted_items}

    if isinstance(obj, list):
        return [sort_json_object(item) for item in obj]

    return obj
