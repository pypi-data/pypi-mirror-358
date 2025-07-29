📢🔬 xxy
========

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Release Building](https://github.com/iaalm/xxy/actions/workflows/release.yml/badge.svg)](https://github.com/iaalm/xxy/actions/workflows/release.yml)
[![PyPI version](https://badge.fury.io/py/xxy.svg)](https://badge.fury.io/py/xxy)

A financial statement analysis tool.

## Run

### Run in shell

```shell
uv run xxy rongda -c "000001 平安银行" "用中文，搜索 2023年年度报告 中'分行业情况'里不同“行业”的营业收入和营业成本，汇总到一张表格上"
```

### Host as web service

```shell
make web
XXY_API_KEY=API_KEY make host
```

### Config file
Config file is under `~/.xxy_cfg.json`.

## Development

### Install dependency
```shell
pip install -e .[dev]
```

### Lint
```shell
make format
```

### Test
```shell
make test
```


### Log critiria
| Level | Verbosity | Frequency | Description |
|-------|-----------|-----------|-------------|
| Critial | Always | Once per run | Can't run anymore |
| Error | Always | Once per run | Can continue run, but this is something unexpected |
| Warning | Always | A few time per run | Can continue run, and it's expected issue |
| Success | -v | At most once per run each code line | User should easy to understand |
| Info | -vv | More than once per run each code line | User should easy to understand |
| Debug | -vvv | At most three per second | Technical details for developers |
| Trace | -vvvv | More than three per second | Easy to know where code is hang |
