from dataclasses import dataclass
from logging import getLogger
from requests import get
from json5 import loads, load
from json import dumps
from os.path import dirname, abspath, join

from utils import GITHUB_MIRRORS, convert_sc_config
from DevSidecarConfig import DevSidecarConfig

__all__ = ["SheasCealerConfig", "GithubConfig", "LocalConfig", "excluded_domains"]

logger = getLogger(__name__)

excluded_domains_path = abspath(
    join(dirname(__file__), "..", "assets", "excluded_domains.json5")
)
# 读取 Excluded domains (Domains that should not be proxied now)
with open(excluded_domains_path) as f:
    excluded_domains: list[str] = load(f)
logger.info(f"Loaded excluded_domains from {excluded_domains_path}")


@dataclass
class Config:

    path: str
    name: str
    default_text: str = "{}"

    def __post_init__(self):
        # 加载配置
        logger.info(f"Loaded {self.name} config from {self.path}")

    def save(self, fn: str):
        with open(fn, "w") as f:
            f.write(self.text)
        logger.info(f"Saved {self.name} config to {fn}")

    def download(self, mirrors: list[str]):
        config_text = self.default_text
        for mirror in mirrors:
            if mirror:
                url = f"https://{mirror}/{self.path}"
            else:
                if self.path.startswith("http"):
                    url = self.path
                else:
                    url = f"https://{self.path}"

            try:
                logger.info(f"Trying to download {self.name} config from {url} ...")
                config_text = get(url, timeout=10, allow_redirects=True).text
            except Exception as e:
                logger.warning(f"Failed to download {self.name} config from {url}: {e}")
                continue
            else:

                try:
                    loads(config_text)
                except Exception as e:
                    logger.warning(
                        f"Downloaded {self.name} config from {url} cannot be parsed as JSON5: {e}"
                    )
                    logger.warning("Raw config text:")
                    logger.warning(config_text)
                    continue
                else:
                    logger.info(f"Downloaded latest {self.name} config from {url}")
                    return config_text
        raise RuntimeError(
            f"Failed to download a valid {self.name} config from all mirrors: {mirrors}"
        )


class SheasCealerConfig(Config):
    def __post_init__(self):
        self.default_text = "[]"
        self.raw_text = self.download(GITHUB_MIRRORS)

        # 解析 sc_config
        self.config = convert_sc_config(self.raw_text, excluded_domains)
        self.text = dumps(self.config, ensure_ascii=False, indent=2)
        logger.info(f"Converted Sheas Cealer config to Dev-Sidecar config")
        super().__post_init__()


class LocalConfig(Config):
    def __post_init__(self):
        with open(self.path) as f:
            self.text = f.read()
            self.config = DevSidecarConfig(loads(self.text))
        super().__post_init__()


class GithubConfig(Config):
    def __post_init__(self):
        self.text = self.download(GITHUB_MIRRORS)
        self.config = DevSidecarConfig(loads(self.text))
        super().__post_init__()


class RemoteConfig(Config):
    def __post_init__(self):
        self.text = self.download([""])
        self.config = DevSidecarConfig(loads(self.text))
        super().__post_init__()
