
from odoo import fields, models, api, _
from ..reservation.new_reservation import  Reservation 
class Command(models.AbstractModel):
    _name = 'command'

    def execute(self, project_task):
        pass

    def undo(self):
        pass
    
    def message(self):
        pass 

class CommandReservationConfirmation(models.TransientModel,Command):
    _name = 'command.reservation_confirmation'
    def execute(self, project_task):
        return project_task.get_confirmation_wizard('option')

class CommandOption(models.TransientModel,Command):
    _name = 'command.option'
    def execute(self, project_task):
        return self.env['command.reservation_confirmation'].execute(project_task)
        CommandReserve().execute(project_task)
            

class CommandReserve(models.TransientModel,Command):
    _name = 'command.reserve'
    def execute(self, project_task):
        import ipdb; ipdb.set_trace()
        reservation = self.env['project.newreservation'].create(self.get_values_from_project_task(project_task))
        new_event = reservation.do_reservation()

        # CommandSendMessage('option')
        # if self.task_state not in ['option', 'done']:
        #     self.send_message('option')
        project_task.write({
            'reservation_event_id': new_event,
            'task_state': 'option'})
    
    def get_values_from_project_task(self, project_task):
        return{
            'date_start': project_task.date_start,
            'date_end': project_task.date_end,
            'complete_name': project_task.complete_name,
            'resource_type': project_task.resource_type,
            'room_id': project_task.room_id.id if project_task.room_id else None,
            'equipment_id': project_task.equipment_id.id if  project_task.equipment_id else None,
            'employee_ids': [(6, 0, project_task.employee_ids.ids)],
            'partner_id': project_task.partner_id.id,
            'client_type': project_task.client_type.id,
            'task_id': project_task.id,
            'sector_id': project_task.sector_id.id if project_task.sector_id else None,
            'category_id': project_task.category_id.id,
        }

class CommandSendMessage(models.TransientModel,Command):
    def execute(self, project_task):
        pass