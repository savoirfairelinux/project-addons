from odoo import fields, models, api, _


class StateFactory(models.AbstractModel):
    _name  = 'state.factory'
    def get_state_instance(self, state):
        if state == 'draft':
            return self.env['task.state.draft']
        if state == 'option':
            return self.env['task.state.option']
        if state == 'postponed':
            return self.env['task.state.postponed']
        if state == 'read':
            return self.env['task.state.read']
        if state == 'done':
            return self.env['task.state.done']
        if state == 'accepted':
            return self.env['task.state.accepted']
        if state == 'canceled':
            return self.env['task.state.canceled']
        if state == 'requested':
            return self.env['task.state.requested']