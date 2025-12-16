# Copilot Instructions for config_convert

## Project purpose

- Converts multiple upstream Dev-Sidecar configs into one merged config published at assets/final_config.json.
- Merge order matters: default_remote → 8odream → Sheas Cealer → manual, then remove excluded_domains entries (left-to-right precedence).

## Key modules

- src/main.py: CLI entrypoint (`--debug` enables verbose logging). Loads excluded_domains.json5, instantiates configs, merges via ExtendedDict operators, writes sorted JSON to final_config_path.
- src/Config.py: Config base class (download helpers using GitHub mirrors, JSON5 parsing). Subclasses: RemoteConfig (generic URL), GithubConfig (GitHub path with mirrors), LocalConfig (local JSON5), SheasCealerConfig (transforms Cealer list into Dev-Sidecar `server.intercepts` + `preSetIpList`, skipping IPv6 when header.skip_IPv6).
- src/ExtendedDict.py: `__add__` deep-merges dicts iteratively (rewrite=True default overwrites existing keys); `__sub__` removes keys recursively; returned type always ExtendedDict for chaining.
- src/utils.py: `is_ipv6_address` handles bracketed literals; `sort_json_object` sorts mapping keys by length desc then alphabetically to stabilize output; `show_raw_text_for_debugging` truncates to 500 chars.
- src/header.py: Central paths (manual_config.json5, excluded_domains.json5, final_config.json) and mirror lists; requires Python 3.14+ per pyproject.toml.

## Behaviors & conventions

- Merging relies on ExtendedDict semantics; if you change precedence, adjust ordering in src/main.py.
- Excluded domains are removed after all additions (`final_config = a + b + c + d - excluded_domains`).
- SheasCealer conversion: domain list cleaned (strips $/#, skips entries containing ^), joined with |; empty SNI becomes "none"; empty target becomes 127.0.0.1; only non-IPv6 targets added to `preSetIpList` when skip_IPv6.
- Output serialization: ensure_ascii=False, indent=2, and key sorting via sort_json_object before writing (match existing format for diffs/automation).
- 对话与代码注释请使用中文，日志输出维持既有英文格式。

## Local workflow

- Setup: Python 3.14+, `pip install -r requirements.txt` (exported from uv). json5 and requests are required.
- Run: `python src/main.py` (add `--debug` for verbose). Output writes to assets/final_config.json alongside manual and excluded files in assets/.

## Extending safely

- When adding new sources, prefer new Config subclasses or reuse GithubConfig/RemoteConfig; always call Config.download with mirrors to avoid single-point failures.
- If changing save logic, consider reusing Config.save to keep formatting consistent with main.py TODO.
- Maintain mirror lists in header.py; skip_IPv6 controls IPv6 handling globally.

## CI/Git flow

- dev branch for changes; main is protected/production. Actions push merged config to main using PAT. Keep output deterministic (sorting) to avoid noisy diffs.
