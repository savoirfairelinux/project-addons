
from odoo import fields, models, api, _

MSG_RES = 'The following resources are already booked:<br>'
MSG_CONFIRM = 'Please confirm your reservation.<br>'
MSG_CONTINUE = 'Do you want to continue?'

class Reservation(models.TransientModel):
    _name = 'project.reservation'

    def reserve_resource(self, resource):
        import ipdb; ipdb.set_trace()
        print("reservation")
        try:
            pass
        except:
            pass

    @api.multi
    def get_confirmation_wizard(self, action, task):
        self.ensure_one()
        res = self.get_booked_resources()
        if res != '':
            res = _(MSG_RES) + res
        message = _(MSG_CONFIRM) + res + _(MSG_CONTINUE)
        new_wizard = self.env['reservation.validation.wiz'].create(
            {
                'task_id': task.id,
                'message': message,
                'action': action,
            }
        )
        return {
            'name': 'Confirm reservation',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reservation.validation.wiz',
            'target': 'new',
            'res_id': new_wizard.id,
        }

    def get_booked_resources(self, task):
        res = ''
        if task.is_type_task() and task.is_resource_booked():
            res += task.room_id.name + '<br>' if (
                task.room_id) else task.equipment_id.name + '<br>'
        for attendee in task.get_partners():
            hres = task.is_hr_resource_double_booked(attendee)
            partner_attendee = self.env['res.partner'].browse(attendee)
            if hres and partner_attendee:
                res += partner_attendee.name + '<br>'
        if task.is_activity():
            for child in task.child_ids:
                if child.is_resource_booked():
                    res += child.room_id.name + \
                        ' - ' + child.date_start + \
                        ' - ' + child.date_end + \
                        ' - ' + child.code + \
                        '<br>' if child.room_id else (
                            child.equipment_id.name + ' - ' +
                            child.date_start + ' - ' + child.date_end +
                            ' - ' + child.code + '<br>')
                for attendee in child.get_partners():
                    hres = child.is_hr_resource_double_booked(attendee)
                    attendee_partner = self.env['res.partner'].browse(attendee)
                    if hres and attendee_partner:
                        res += attendee_partner.name + \
                            ' - ' + child.date_start + \
                            ' - ' + child.date_end + \
                            ' - ' + child.code + \
                            '<br>'
        return res
    
    def is_resource_booked(self, task):
        if task.room_id:
            overlaps = self.env['calendar.event'].search([
                ('room_id', '=', task.room_id.id),
                ('start', '<', task.date_end),
                ('stop', '>', task.date_start),
                ('state', '!=', 'cancelled'),
            ])
            overlaps_ids = overlaps.ids
            for calendar_event in overlaps_ids:
                if self.env['calendar.event'] \
                        .browse(calendar_event).event_task_id.id == task.id:
                    overlaps_ids.remove(calendar_event)
            if len(overlaps_ids) > 0:
                return True
        if task.equipment_id:
            overlaps_equipment = self.env['calendar.event'].search([
                ('equipment_ids', 'in', [task.equipment_id.id]),
                ('start', '<', task.date_end),
                ('stop', '>', task.date_start),
                ('state', '!=', 'cancelled'),
            ])
            if len(overlaps_equipment) > 0:
                return True
        return False

    @api.multi
    def request_reservation(self):
        self.ensure_one()
        calendar_event = self.env['calendar.event']
        values = {
            'start': self.date_start,
            'stop': self.date_end,
            'name': self.complete_name,
            'resource_type': self.resource_type,
            'room_id': self.room_id.id if self.room_id else None,
            'equipment_ids': [(
                4, self.equipment_id.id, 0)] if self.equipment_id else None,
            'partner_ids': [(6, 0, self.get_partners())],
            'client_id': self.partner_id.id,
            'client_type': self.client_type.id,
            'state': 'open',
            'event_task_id': self.id,
            'is_task_event': True,
            'sector_id': self.sector_id.id if self.sector_id else None,
            'category_id': self.category_id.id,
        }
        new_event = calendar_event.create(values)
        self.reservation_event_id = new_event.id
        if self.room_id:
            self.reserve_equipment_inside(new_event.id)
