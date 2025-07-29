"""
pdm-plugin-i

A PDM plugin that support `pdm i` as alias of `pdm install`
:author: Waket Zheng <waketzheng@gmail.com>
:license: MIT
"""

from pdm.core import Core

from .command import Command

__version__ = "0.2.0"


def plugin(core: Core) -> None:
    core.register_command(Command)
