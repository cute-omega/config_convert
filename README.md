# Sheas Cealer 转 Dev-Sidecar 的配置转换器

把Sheas Cealer的配置文件转换成Dev-Sidecar的配置文件，并支持与其他Dev-Sidecar配置合并。目前由GitHub Actions自动执行，当前每30分钟更新一次配置。

## 用法：
把https://cute-omega.github.io/other-assets/ds-config.json 填入dev-sidecar的个人远程配置，然后点击“更新远程配置”以立即生效。之后dev-sidecar会在每次启动时自动更新配置。

## 脚本当前工作流：

`8odream.config + sheas_cealer.config + postset.config - ExcludedDomains`

`8odream.config`来自[8odream/Dev-sidecar-8odream-config](https://github.com/8odream/Dev-sidecar-8odream-config)

`sheas_cealer.config`来自[SpaceTimee/Cealing-Host](https://github.com/SpaceTimee/Cealing-Host)

`postset.config`是本仓库手动配置的后置设置文件，包含一些额外的配置调整。

代码已经得到优化，更方便的支持扩展其他所需合并的配置文件。

## 本地运行

尽管这看起来是显而易见的，我们仍然给出运行脚本的步骤。

```bash
git clone https://github.com/cute-omega/config_convert.git
cd config_convert
pip3 install -r requirements.txt
python3 main.py
```

## 开发
请Fork dev分支，更新也请向dev分支发PR。

推送PR前请在本地测试无bug后进行。

main分支仅用于生产用途。

## GitHub Actions 配置

本仓库使用GitHub Actions自动运行配置转换并推送到main分支。由于main分支有分支保护规则，工作流使用Personal Access Token (PAT)来绕过这些规则。

### 所需的Secrets配置：
- `PAT`: 具有repo权限的Personal Access Token，用于向main分支推送更改
