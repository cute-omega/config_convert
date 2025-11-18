from json import dump
import logging
from os.path import abspath

from Config import SheasCealerConfig, RemoteConfig, LocalConfig, ExcludedDomains

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] File %(filename)s, line %(lineno)s, in %(module)s.%(funcName)s\n\t%(message)s",
)

preset_fn = "ds-preset.json5"
postset_fn = "ds-postset.json5"
ds_fn = "ds-config.json"


def main():

    # 获取 Sheas Cealer 配置，默认为空列表
    sheas_cealer = SheasCealerConfig(
        "SpaceTimee/Cealing-Host/raw/main/Cealing-Host.json", "Sheas Cealer", "[]"
    )

    # 读取 8odream 配置
    _8odream = RemoteConfig(
        "8odream/Devsidecar-8odream-config/raw/main/config.json", "PreSet", "{}"
    )
    _8odream.save(preset_fn)

    # 读取 postset 配置
    postset = LocalConfig(postset_fn, "PostSet")

    # 合并配置
    ds_config = _8odream.config + sheas_cealer.config + postset.config - ExcludedDomains
    logging.info("Merged all configs and cleared excluded domain rules")

    # 保存 Dev-Sidecar 配置
    with open(ds_fn, "w") as ds_file:
        dump(ds_config, ds_file, ensure_ascii=False, indent=2)
    logging.info(f"Saved Dev-Sidecar config as {abspath(ds_fn)}")


if __name__ == "__main__":
    main()
