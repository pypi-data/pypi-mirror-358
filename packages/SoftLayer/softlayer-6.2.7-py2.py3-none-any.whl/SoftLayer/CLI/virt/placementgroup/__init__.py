"""Manages Reserved Capacity."""
# :license: MIT, see LICENSE for more details.

import importlib
import os

import click
from SoftLayer.CLI.command import CommandLoader
from SoftLayer.CLI.command import OptionHighlighter

CONTEXT = {'help_option_names': ['-h', '--help'],
           'max_content_width': 999}


class PlacementGroupCommands(CommandLoader):
    """Loads module for placement group related commands.

    Currently the base command loader only supports going two commands deep.
    So this small loader is required for going that third level.
    """

    def __init__(self, **attrs):
        CommandLoader.__init__(self, **attrs)
        self.path = os.path.dirname(__file__)
        self.highlighter = OptionHighlighter()
        self.env = None
        self.console = None

    def list_commands(self, ctx):
        """List all sub-commands."""
        commands = []
        for filename in os.listdir(self.path):
            if filename == '__init__.py':
                continue
            if filename.endswith('.py'):
                commands.append(filename[:-3].replace("_", "-"))
        commands.sort()
        return commands

    def get_command(self, ctx, cmd_name):
        """Get command for click."""
        path = "%s.%s" % (__name__, cmd_name)
        path = path.replace("-", "_")
        try:
            module = importlib.import_module(path)
            return getattr(module, 'cli')
        except ModuleNotFoundError as ex:
            print(ex.name)
            return None


# Required to get the sub-sub-sub command to work.
@click.group(cls=PlacementGroupCommands, context_settings=CONTEXT)
def cli():
    """Base command for all capacity related concerns"""
