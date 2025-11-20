import logging
from json import dump
from json5 import load
import argparse
from header import final_config_path, manual_path, excluded_domains_path
from Config import (
    SheasCealerConfig,
    GithubConfig,
    LocalConfig,
    RemoteConfig,
)

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
    logger.info(f"Loaded excluded_domains from {excluded_domains_path}")

    # 获取 Dev-Sidecar 内置默认远程配置
    default_remote = RemoteConfig(
        "https://gitee.com/wangliang181230/dev-sidecar/raw/docmirror2.x/packages/core/src/config/remote_config.json",
        "Default Remote",
    )

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

    # 合并配置
    final_config = (
        default_remote.config
        + _8odream.config
        + sheas_cealer.config
        + manual.config
        - excluded_domains
    )
    logger.info("Merged all configs and cleared excluded domain rules")

    # 保存 Dev-Sidecar 配置
    # TODO: Consider refactoring this block to use Config.save for saving the final configuration.
    # This would centralize all config-saving logic within the Config class/module, ensuring consistency
    # and reducing code duplication. Specifically, evaluate whether the logic for writing to
    # final_config_path (including formatting options like ensure_ascii and indent) can be encapsulated
    # in Config.save, and update this call to use that method. This will make future changes to the
    # saving process easier to maintain.
    with open(final_config_path, "w") as f:
        dump(final_config, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved final Dev-Sidecar config as {final_config_path}")


if __name__ == "__main__":
    main()
