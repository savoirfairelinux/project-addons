from .project_task_state import Draft, Option,\
     Postponed, Read, Done, Accepted, Canceled, Requested

class StateFactory:
    @staticmethod
    def get_state(state):
        if state == 'draft':
            return Draft()
        if state == 'option':
            return Option()
        if state == 'postponed':
            return Postponed()
        if state == 'read':
            return Read()
        if state == 'Done':
            return Done()
        if state == 'accepted':
            return Accepted()
        if state == 'canceled':
            return Canceled()
        if state == 'requested':
            return Requested()