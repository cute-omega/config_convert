from dataclasses import dataclass, field
from logging import getLogger
from requests import get
from json5 import loads, load
from json import dump


from header import (
    JSON5Object,
    RawSheasCealerConfig,
    GITHUB_MIRRORS,
    skip_IPv6,
)
from utils import (
    is_ipv6_address,
    show_raw_text_for_debugging,
    sort_json_object,
)
from ExtendedDict import ExtendedDict

__all__ = [
    "GithubConfig",
    "LocalConfig",
    "RemoteConfig",
    "SheasCealerConfig",
]


logger = getLogger(__name__)


@dataclass
class Config:
    """dev-sidecar配置类，在初始化时即尝试加载。

    Args:
        path (str): 配置路径，可以是本地路径、GitHub路径（省略协议和域名）或完整的远程URL
        name (str): 配置名称，用于日志记录

    Attributes:
        raw_config (dict | list, initialized during object construction): 仅序列化的原始配置数据
        config (ExtendedDict, initialized during object construction): 解析后的Dev-Sidecar配置
    """

    path: str
    name: str
    raw_config: dict | list = field(init=False)
    config: ExtendedDict = field(init=False)

    def __post_init__(self):
        """
        子类应重写本函数以实现加载配置，并在加载完成后调用 super().__post_init__() 以记录日志。
        Subclasses should override this method to implement configuration loading,
        and call super().__post_init__() at the end to log the loading event.
        """
        logger.info(f"Loaded {self.name} config from {self.path}")

    def save(self, fn: str):
        sorted_config = sort_json_object(self.config)
        with open(fn, "w") as f:
            dump(sorted_config, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {self.name} config to {fn}")

    def download(self, mirrors: list[str]) -> JSON5Object:
        """从远程下载配置并反序列化为JSON5对象，会尝试所有配置的镜像

        Args:
            mirrors (list[str]): 下载时指定的镜像域名列表，可以为空列表

        Raises:
            RuntimeError: 所有镜像下载全部失败，或内容全部不可反序列化

        Returns:
            JSON5Object: 反序列化后的JSON5对象
        """
        for mirror in mirrors:
            if mirror:
                url = f"https://{mirror}/{self.path}"
            else:
                if self.path.startswith("http"):
                    url = self.path
                else:
                    url = f"https://{self.path}"

            r = None
            try:
                logger.info(f"Trying to download {self.name} config from {url} ...")
                r = get(url, timeout=10, allow_redirects=True)
                if r.status_code != 200:
                    raise ValueError(f"HTTP {r.status_code} {r.reason} for {url}")
            except Exception as e:
                logger.warning(f"Failed to download {self.name} config from {url}: {e}")
                if r:
                    logger.debug(f"Request status: {r.status_code} {r.reason}")
                    show_raw_text_for_debugging(self.name, r.text, logger)
                else:
                    logger.debug("No response received.")
                continue
            else:

                config_text = r.text
                try:
                    result: JSON5Object = loads(config_text)
                except Exception as e:
                    logger.warning(
                        f"Downloaded {self.name} config from {url} cannot be parsed as JSON5: {e}"
                    )
                    show_raw_text_for_debugging(self.name, config_text, logger)
                    continue
                else:
                    logger.info(f"Downloaded latest {self.name} config from {url}")
                    return result
        raise RuntimeError(
            f"Failed to download a valid {self.name} config from all mirrors: {mirrors}"
        )  # fast fail


class SheasCealerConfig(Config):
    """
    Sheas Cealer配置，反序列化之后会自动转换。

    raw_config是原始的Sheas Cealer配置list
    """

    def __post_init__(self):
        self.raw_config: RawSheasCealerConfig = self.download(GITHUB_MIRRORS)

        # 解析 raw_config
        self.config = self.__convert()
        logger.info(f"Converted Sheas Cealer config to Dev-Sidecar config")
        super().__post_init__()

    def __convert(self) -> ExtendedDict:
        """
        Convert the raw Sheas Cealer configuration to Dev-Sidecar format.

        Iterates over each entry in self.raw_config, extracting domain rules, SNI, and target IPs.
        - Domains are cleaned and combined into a single rule string.
        - SNI values are set for each domain rule.
        - Target IPs are added to the preSetIpList if they are not IPv6 (when skip_IPv6 is enabled).

        Returns:
            ExtendedDict: The configuration in Dev-Sidecar format, with 'server', 'intercepts', and 'preSetIpList' sections populated.
        """
        ds_config = ExtendedDict({"server": {"intercepts": {}, "preSetIpList": {}}})

        for item in self.raw_config:
            sni: str | None = item[1]
            if sni is None:
                continue
            elif sni == "":
                sni = "none"

            target: str = item[2]
            if target == "":
                target = "127.0.0.1"

            is_IPv6 = is_ipv6_address(target)

            raw_domains: list[str] = item[0]
            domains = [
                raw_domain.lstrip("$#")
                for raw_domain in raw_domains
                if "^" not in raw_domain
            ]

            for domain in domains:
                intercepts = ds_config["server"].setdefault("intercepts", {})
                domain_dict = intercepts.setdefault(domain, {})
                sni_dict = domain_dict.setdefault(".*", {})
                sni_dict["sni"] = sni

                if skip_IPv6 and not is_IPv6:
                    pre_set_ip_list = ds_config["server"].setdefault("preSetIpList", {})
                    pre_set_domain_dict = pre_set_ip_list.setdefault(domain, {})
                    pre_set_domain_dict[target] = True

        return ds_config


class LocalConfig(Config):
    """
    本地配置

    path应指定为本地文件路径。
    """

    def __post_init__(self):
        with open(self.path) as f:
            self.raw_config = load(f)
            self.config = ExtendedDict(self.raw_config)
        super().__post_init__()


class GithubConfig(Config):
    """
    GitHub配置，下载时会自动尝试内置的GitHub镜像。

    path应为省略协议和域名的GitHub URL，如"user/repo/raw/branch/path/to/config.json5"
    """

    def __post_init__(self):
        self.raw_config: JSON5Object = self.download(GITHUB_MIRRORS)
        self.config = ExtendedDict(self.raw_config)
        super().__post_init__()


class RemoteConfig(Config):
    """普通的远程配置

    path应为完整的远程URL。
    """

    def __post_init__(self):
        self.raw_config: JSON5Object = self.download([""])
        self.config = ExtendedDict(self.raw_config)
        super().__post_init__()
