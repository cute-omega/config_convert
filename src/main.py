import logging
from json import dump
from json5 import load
import argparse
from datetime import timezone, timedelta, datetime

from header import final_config_path, manual_path, excluded_domains_path
from Config import (
    SheasCealerConfig,
    GithubConfig,
    LocalConfig,
    RemoteConfig,
    MemoryConfig,
)
from utils import sort_json_object

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    level = logging.DEBUG if args.debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] File %(filename)s, line %(lineno)s, in %(module)s.%(funcName)s\n\t%(message)s",
    )

    # 读取 Excluded domains (Domains that should not be proxied now)
    with open(excluded_domains_path) as f:
        excluded_domains: list[str] = load(f)
    logger.info(f"Finish loading excluded_domains from {excluded_domains_path}")

    try:
        # 获取 Dev-Sidecar 内置默认远程配置
        official = RemoteConfig(
            "https://gitee.com/wangliang181230/dev-sidecar-config/raw/main/remote_config.json",
            "Official",
        )
    except RuntimeError as e:
        logger.error(e)
        logger.warning(
            "Failed to get official config, assume it has not changed and fallback to only update my last result."
        )
        try:
            official = RemoteConfig(
                "https://cute-omega.github.io/other-assets/ds-config.json",
                "Fallback Last Result",
            )
        except RuntimeError as e:
            logger.error(e)
            logger.warning(
                "Failed to get fallback config, assume it has not changed and fallback to local file."
            )
            official = LocalConfig(final_config_path, "Local Last Result")

    # 获取 Sheas Cealer 配置，默认为空列表
    sheas_cealer = SheasCealerConfig(
        "SpaceTimee/Cealing-Host/raw/main/Cealing-Host.json", "Sheas Cealer"
    )

    # 读取 8odream 配置
    _8odream = GithubConfig(
        "8odream/Devsidecar-8odream-config/raw/main/config.json", "8odream"
    )

    # 读取 手动配置
    manual = LocalConfig(manual_path, "Manual")
    # 配置版本应是“GMT+8的开始编辑时间，固定位数为年月日+时分”（年四位，月份两位，日期两位，小时两位，分钟两位），并且是JSON意义上的number类型
    config_version = int(
        datetime.now(tz=timezone(timedelta(hours=8))).strftime("%Y%m%d%H%M")
    )
    manual.config["app"]["metaInfo"]["version"] = config_version

    # 合并配置
    final_config = (
        manual.config
        + sheas_cealer.config
        + _8odream.config
        + official.config
        - excluded_domains
    )
    logger.info("Finish merging all configs and clearing excluded domain rules")

    # 保存 Dev-Sidecar 配置
    sorted = sort_json_object(final_config)
    FinalSorted = MemoryConfig("Memory", "Final Sorted", sorted)
    FinalSorted.save(final_config_path)


if __name__ == "__main__":
    main()
