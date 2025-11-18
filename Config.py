from dataclasses import dataclass
from logging import getLogger
from requests import get
from json5 import loads, load
from json import dumps

from utils import GITHUB_MIRRORS, convert_sc_config
from DevSidecarConfig import DevSidecarConfig

__all__ = ["SheasCealerConfig", "RemoteConfig", "LocalConfig", "ExcludedDomains"]

logger = getLogger(__name__)

ExcludedDomains_fn = "ExcludedDomains.json5"
# 读取 ExcludedDomains (Domains that should not be proxied now)
with open(ExcludedDomains_fn) as ExcludedDomains_file:
    ExcludedDomains: list[str] = load(ExcludedDomains_file)
logger.info(f"Loaded ExcludedDomains from {ExcludedDomains_fn}")


@dataclass
class Config:

    path: str
    name: str
    default_text: str = ""

    def __post_init__(self):
        # 加载配置
        logger.info(f"Loaded {self.name} config from {self.path}")

    def save(self, fn: str):
        with open(fn, "w") as f:
            f.write(self.text)
        logger.info(f"Saved {self.name} config to {fn}")

    def download(self, mirrors=GITHUB_MIRRORS):
        config_text = self.default_text
        for mirror in mirrors:
            url = f"https://{mirror}/{self.path}"

            try:
                logger.info(f"Trying to download {self.name} config from {url} ...")
                config_text = get(url, timeout=10, allow_redirects=True).text
            except Exception as e:
                logger.error(f"Failed to download {self.name} config from {url}: {e}")
                continue
            else:

                try:
                    loads(config_text)
                except Exception as e:
                    logger.error(
                        f"Downloaded {self.name} config from {url} is invalid: {e}"
                    )
                    continue
                else:
                    logger.info(f"Downloaded latest {self.name} config from {url}")
                    return config_text
        raise RuntimeError(
            f"Failed to download a valid {self.name} config from all mirrors: {mirrors}"
        )


class SheasCealerConfig(Config):
    def __post_init__(self):
        self.raw_text = self.download(GITHUB_MIRRORS)

        # 解析 sc_config
        self.config = convert_sc_config(self.raw_text, ExcludedDomains)
        self.text = dumps(self.config, ensure_ascii=False, indent=2)
        logger.info(f"Converted Sheas Cealer config to Dev-Sidecar config")
        super().__post_init__()


class LocalConfig(Config):
    def __post_init__(self):
        with open(self.path) as f:
            self.text = f.read()
            self.config = DevSidecarConfig(loads(self.text))
        super().__post_init__()


class RemoteConfig(Config):
    def __post_init__(self):
        self.text = self.download(GITHUB_MIRRORS)
        self.config = DevSidecarConfig(loads(self.text))
        super().__post_init__()
