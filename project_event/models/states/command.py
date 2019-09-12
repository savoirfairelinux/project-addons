
from odoo import fields, models, api, _

class Command:

    def execute(self, project_task):
        pass

    def undo(self):
        pass
    
    def message(self):
        pass 

class CommandOption(Command):
    def execute(self, project_task):
        return project_task.get_confirmation_wizard('option')
