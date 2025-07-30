from pdm.cli.commands.install import Command as _Command


class Command(_Command):
    """Install dependencies from lock file(shortcut of 'install')"""

    name = "i"
