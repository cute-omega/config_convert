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
    logger.info(f"Loaded excluded_domains from {excluded_domains_path}")

    try:
        # 获取 Dev-Sidecar 内置默认远程配置
        default_remote = RemoteConfig(
            "https://gitee.com/wangliang181230/dev-sidecar/raw/docmirror2.x/packages/core/src/config/remote_config.json",
            "Default Remote",
        )
    except RuntimeError as e:
        logger.error(e.args[0])
        logger.warning(
            "Cannot get default remote config, assert it not changed and fallback to only update my last result."
        )
        default_remote = RemoteConfig(
            "https://cute-omega.github.io/other-assets/ds-config.json",
            "Fallback Last Result",
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
    # TODO: 考虑将此代码块重构为使用 Config.save 来保存最终配置。
    # 这样可以将所有配置保存逻辑集中到 Config 类/模块中，保证一致性并减少重复代码。
    # 具体来说，请评估将写入 final_config_path 的逻辑（包括 ensure_ascii 和 indent 等格式化选项）
    # 是否可以封装到 Config.save 中，并将此处的写入调用替换为该方法。这样可以让将来对保存流程的
    # 修改更易维护。
    sorted_final_config = sort_json_object(final_config)
    with open(final_config_path, "w") as f:
        dump(sorted_final_config, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved final Dev-Sidecar config as {final_config_path}")


if __name__ == "__main__":
    main()
