from .command import CommandOption
from odoo import fields, models, api, _


class ProjectTaskState(models.AbstractModel):
    _name = 'task.state'
    name = 'state'
    allowed = []

    def change_state(self, state):
        if state.name in self.allowed:
            self.__class__ = state
        else:
            return False
    
    def __str__(self):
        return self.name

class Draft(ProjectTaskState):
    _name = 'task.state.draft'
    name = 'draft'
    allowed = ['option']
    def change_state(self, project_task, state):
        super().change_state(state)

        return self.env['command.option'].execute(project_task)

    def __del__(self): 
        print("die draft") 

class Option(ProjectTaskState):
    _name = 'task.state.option'
    name = 'option'
    allowed = ['requested','postponed','canceled']
    
    def change_state(self, state):
        CommandOption().execute(state)
        super().change_state(state)

    def __del__(self): 
        print("die option") 

class Requested(ProjectTaskState):
    _name = 'task.state.requested'
    name = 'requested'
    allowed = ['option','accepted','read','postponed','canceled']
    def change_state(self, state):
        CommandRequest().execute(state)
        super().change_state(state)

class Accepted(ProjectTaskState):
    _name = 'task.state.accepted'

    name = 'accepted'
    allowed = ['option','done','postponed','canceled']

class Done(ProjectTaskState):
    _name = 'task.state.done'

    name = 'done'
    allowed = ['']

class Read(ProjectTaskState):
    _name = 'task.state.read'

    name = 'read'
    allowed = ['option','requested','accepted','done','postponed','canceled']

class Postponed(ProjectTaskState):
    _name = 'task.state.postponed'

    name = 'postponed'
    allowed = ['option','requested','canceled']

class Canceled(ProjectTaskState):
    _name = 'task.state.canceled'

    name = 'canceled'
    allowed = ['option','requested','postponed']