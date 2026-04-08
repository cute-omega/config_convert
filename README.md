# Sheas Cealer 转 Dev-Sidecar 的配置转换器

把Sheas Cealer的配置文件转换成Dev-Sidecar的配置文件，并支持与其他Dev-Sidecar配置合并。目前由GitHub Actions自动执行，当前每8小时更新一次配置。

## 用法

把<https://cute-omega.github.io/other-assets/ds-config.json> 填入dev-sidecar的个人远程配置，然后点击“更新远程配置”以立即生效。之后dev-sidecar会在每次启动时自动更新配置。

## 脚本当前工作流

`official.config + 8odream.config + sheas_cealer.config + manual.config - excluded_domains`

`official.config`来自[Dev-Sidecar内置的默认远程配置地址](https://gitee.com/wangliang181230/dev-sidecar/raw/docmirror2.x/packages/core/src/config/remote_config.json)

`8odream.config`来自[8odream/Dev-sidecar-8odream-config](https://github.com/8odream/Dev-sidecar-8odream-config)

`sheas_cealer.config`转换自[SpaceTimee/Cealing-Host](https://github.com/SpaceTimee/Cealing-Host)

`manual.config`是[本仓库手动配置的收尾设置文件](https://github.com/cute-omega/config_convert/blob/main/assets/manual_config.json5)，包含一些额外的配置调整。

**注意**：示范中的加法不满足交换律，从左向右结合。右边的配置效力高于左边的。

代码已经得到优化，更方便的支持扩展其他所需合并的配置文件。

## 本地运行

尽管这看起来是显而易见的，我们仍然给出运行脚本的步骤。

```bash
git clone https://github.com/cute-omega/config_convert.git
cd config_convert
pip3 install -r requirements.txt
python3 src/main.py
```
最好用`uv sync`同步环境，`requirements.txt`未必及时更新。

## 开发

请Fork dev分支，更新也请向dev分支发PR。

推送PR前请在本地测试无bug后进行。

main分支仅用于生产用途。

## GitHub Actions 配置

本仓库使用GitHub Actions自动运行配置转换并推送到main分支。由于main分支有分支保护规则，工作流使用Personal Access Token (PAT)来绕过这些规则。

### 所需的Secrets配置

- `PAT`: 具有repo权限的Personal Access Token，用于向main分支推送更改
