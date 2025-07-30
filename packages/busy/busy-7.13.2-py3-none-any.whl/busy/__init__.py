import sys
from wizlib.app import WizApp
from wizlib.ui_handler import UIHandler
from wizlib.config_handler import ConfigHandler
from wizlib.command import WizHelpCommand

from busy.command import BusyCommand
from busy.storage.file_storage import FileStorage


class BusyApp(WizApp):

    base = BusyCommand
    name = 'busy'
    handlers = [UIHandler, ConfigHandler]

    def __init__(self, **handlers):
        super().__init__(**handlers)
        self.storage = FileStorage(self.config.get('busy-storage-directory'))

    def run(self, **vals):
        super().run(**vals)

    # For MCP server. Probably belongs in WizLib.
    def do(self, command_string) -> dict:
        args = command_string.split(' ')
        ns = self.parser.parse_args(args)
        vals = vars(ns)
        if 'help' in vals:
            ccls = WizHelpCommand
        else:
            c = 'command'
            cname = (vals.pop(c) if c in vals else None) or self.base.default
            ccls = self.base.family_member('name', cname)
            if not ccls:
                raise Exception(f"Unknown command {cname}")
        command = ccls(self, **vals)
        result = command.execute()
        return {'result': result, 'status': command.status}
