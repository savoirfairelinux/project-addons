from .command import CommandOption


class ProjectTaskState:
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
    name = 'draft'
    allowed = ['option']
    def change_state(self, project_task, state):
        super().change_state(state)

        return CommandOption().execute(project_task)

    def __del__(self): 
        print("die draft") 

class Option(ProjectTaskState):
    name = 'option'
    allowed = ['requested','postponed','canceled']
    def change_state(self, state):
        CommandOption().execute(state)
        super().change_state(state)

    def __del__(self): 
        print("die option") 

class Requested(ProjectTaskState):
    name = 'requested'
    allowed = ['option','accepted','read','postponed','canceled']

class Accepted(ProjectTaskState):
    name = 'accepted'
    allowed = ['option','done','postponed','canceled']

class Done(ProjectTaskState):
    name = 'done'
    allowed = ['']

class Read(ProjectTaskState):
    name = 'read'
    allowed = ['option','requested','accepted','done','postponed','canceled']

class Postponed(ProjectTaskState):
    name = 'postponed'
    allowed = ['option','requested','canceled']

class Canceled(ProjectTaskState):
    name = 'canceled'
    allowed = ['option','requested','postponed']