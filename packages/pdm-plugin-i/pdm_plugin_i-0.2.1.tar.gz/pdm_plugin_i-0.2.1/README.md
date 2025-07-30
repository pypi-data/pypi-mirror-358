# pdm-plugin-i

[![Tests](https://github.com/waketzheng/pdm-plugin-i/workflows/Tests/badge.svg)](https://github.com/waketzheng/pdm-plugin-i/actions?query=workflow%3Aci)
[![pypi version](https://img.shields.io/pypi/v/pdm-plugin-i.svg)](https://pypi.org/project/pdm-plugin-i/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/waketzheng/pdm-plugin-i/main.svg)](https://results.pre-commit.ci/latest/github/waketzheng/pdm-plugin-i/main)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm-project.org)

A PDM plugin that add command `pdm i` as alias of `pdm install`

## Requirements

pdm-plugin-i requires Python >=3.9

## Installation

On PDM 2.25+, you can install the plugin directly by:

```bash
$ pdm self add pdm-plugin-i
```

If you have installed PDM with the recommended tool `pipx`, add this plugin by:

```bash
$ pipx inject pdm pdm-plugin-i
```

Or if you have installed PDM with `pip install --user pdm`, install with `pip` to the user site:

```bash
$ python -m pip install --user pdm-plugin-i
```

Otherwise, install `pdm-plugin-i` to the same place where PDM is located.

## Usage

```
$ pdm i
```

**Common Options:**

The same as `pdm install`

## Changelog

See [CHANGELOG.md](https://github.com/waketzheng/pdm-plugin-i/blob/main/CHANGELOG.md)
