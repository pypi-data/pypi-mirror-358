from pdm.cli.commands.install import Command as _Command


class Command(_Command):
    """Act `pdm i` as `pdm install`"""

    name = "i"
