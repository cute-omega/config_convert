from json5 import dump, load, loads
import logging
from requests import get
from requests.exceptions import SSLError, ConnectTimeout, ReadTimeout, Timeout
from os.path import abspath

from DevSidecarConfig import DevSidecarConfig
from SheasCealerConfigParser import parse_sc_config
from utils import sc_config_type

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

preset_fn = "ds-preset.json5"
postset_fn = "ds-postset.json5"
ds_fn = "ds-config.json5"
ExcludedDomains_fn = "ExcludedDomains.json5"

# Domains that should not be proxied now
# 读取 ExcludedDomains
with open(ExcludedDomains_fn) as ExcludedDomains_file:
    ExcludedDomains: list[str] = load(ExcludedDomains_file)
logging.info(f"Loaded ExcludedDomains from {abspath(ExcludedDomains_fn)}")


def main():

    sc_urls = ["https://github.com/SpaceTimee/Cealing-Host/raw/main/Cealing-Host.json"]
    sc_urls.append(
        sc_urls[0].replace(
            "https://github.com", "https://ghfast.top/https://github.com"
        )
    )
    sc_urls.append(sc_urls[0].replace("github.com", "xget.xi-xu.me/gh"))

    # 获取 Sheas Cealer 配置
    sc_config_text = "[]"  # 默认空列表
    for sc_url in sc_urls:
        try:
            logging.info(f"Trying to download Sheas Cealer config from {sc_url} ...")
            sc_config_text = get(sc_url, timeout=10).text
        except (ConnectTimeout, Timeout, ReadTimeout, SSLError) as e:
            logging.error(f"Failed to download Sheas Cealer config from {sc_url}: {e}!")
        else:
            logging.info(f"Downloaded latest Sheas Cealer config from {sc_url}")
            break
    sc_config: sc_config_type = loads(sc_config_text)

    # 读取 preset_config
    with open(preset_fn) as preset_file:
        preset_config = DevSidecarConfig(load(preset_file))
    logging.info(f"Loaded preset config from {abspath(preset_fn)}")

    # 解析 sc_config
    # 此处引用ExcludedDomains是很烦人的一个依赖，希望未来可以完全用postset_config代替，至少也要改用最后的剔除逻辑
    converted_config = parse_sc_config(sc_config, ExcludedDomains)
    logging.info(f"Converted Sheas Cealer config to Dev-Sidecar config")

    # 读取 postset_config
    with open(postset_fn) as postset_file:
        postset_config = DevSidecarConfig(load(postset_file))
    logging.info(f"Loaded postset config from {abspath(postset_fn)}")

    # 合并配置
    ds_config = preset_config + postset_config + converted_config - ExcludedDomains
    logging.info("Cleared all excluded domain rules")

    # 保存 Dev-Sidecar 配置
    with open(ds_fn, "w") as ds_file:
        dump(ds_config, ds_file, ensure_ascii=False, indent=2)
    logging.info(f"Saved Dev-Sidecar config as {abspath(ds_fn)}")


if __name__ == "__main__":
    main()
