
from odoo import fields, models, api, _

MSG_RES = 'The following resources are already booked:<br>'
MSG_CONFIRM = 'Please confirm your reservation.<br>'
MSG_CONTINUE = 'Do you want to continue?'

class Reservation(models.TransientModel):
    _name = 'project.reservation'

    reservation_event_id = fields.Integer(
        string='Reservation event',
    )
    date_start = fields.Datetime(
        string='Starting Date',
        default=None,
        index=True,
        copy=False,
        track_visibility='onchange',
    )
    date_end = fields.Datetime(
        string='Ending Date',
        index=True,
        copy=False,
        track_visibility='onchange',
    )
    resource_type = fields.Selection([
        ('user', 'Human'),
        ('equipment', 'Equipment'),
        ('room', 'Room')],
        string='Resource Type',
        default='room',
        track_visibility='onchange',
    )
    employee_ids = fields.Many2many(
        'hr.employee', 'task_emp_rel',
        'task_id', 'employee_id',
        string='Employees',
        track_visibility='onchange',
    )
    client_type = fields.Many2one(
        'res.partner.category.type',
        string='Client Type',
        track_visibility='onchange',
    )
    responsible_id = fields.Many2one(
        'res.partner',
        string='Task/Activity Responsible',
        track_visibility='onchange',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        track_visibility='onchange',
    )
    sector_id = fields.Many2one(
        'res.partner.sector',
        string='Faculty Sector',
        track_visibility='onchange',
    )
    category_id = fields.Many2one(
        'task.category',
        string='Category',
        default=lambda self: self.env['task.category'].search(
            [('is_default', '=', True)]),
        track_visibility='onchange',
    )
    room_id = fields.Many2one(
        string='Room',
        comodel_name='resource.calendar.room',
        ondelete='set null',
        track_visibility='onchange',
    )
    equipment_id = fields.Many2one(
        string='Equipment',
        comodel_name='resource.calendar.instrument',
        ondelete='set null',
        track_visibility='onchange',
    )
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
        res = self.get_booked_resources(task)
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


    def get_booked_resources(self):
        res = ''
        if self.is_type_task() and self.is_resource_booked():
            res += self.room_id.name + '<br>' if (
                self.room_id) else self.equipment_id.name + '<br>'
        for attendee in self.get_partners():
            hres = self.is_hr_resource_double_booked(attendee)
            partner_attendee = self.env['res.partner'].browse(attendee)
            if hres and partner_attendee:
                res += partner_attendee.name + '<br>'
        if self.is_activity():
            for child in self.child_ids:
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



#=========self=project_task==============================================================

    @api.multi
    def update_reservation_event(self, vals):
        if len(self) == 1:
            if self.reservation_event_id:
                reservation_event = self.env['calendar.event']. \
                    browse(self.reservation_event_id)
                field_names = [
                    'date_start', 'date_end', 'equipment_id',
                    'name', 'resource_type', 'room_id', 'client_type',
                    'employee_ids', 'sector_id', 'category_id', 'partner_id',
                ]
                reservation_event.write(
                    self.set_value_reservation_event(field_names, vals)
                )

    def set_value_reservation_event(self, field_names, vals):
        update_vals = {}
        for index in range(0, len(field_names)):
            if field_names[index] in vals:
                if field_names[index] == 'partner_id':
                    update_vals['client_id'] = vals[field_names[index]]
                if field_names[index] == 'date_start':
                    update_vals['start'] = vals[field_names[index]]
                if field_names[index] == 'date_end':
                    update_vals['stop'] = vals[field_names[index]]
                if field_names[index] == 'equipment_id' \
                        and vals['equipment_id']:
                    update_vals.update(self.update_value_equipment_id(vals))
                elif field_names[index] == 'room_id':
                    if vals['room_id']:
                        update_vals.update(self.update_value_room_id(vals))
                    update_vals[field_names[index]] = vals[field_names[index]]
                if field_names[index] == 'employee_ids':
                    update_vals['partners_ids'] = self\
                        .get_partners()
                    update_vals.update(self.update_value_employee_ids(vals))
                if field_names[index] in ('sector_id',
                                          'category_id',
                                          'resource_type',
                                          'name',
                                          'client_type'):
                    update_vals[field_names[index]] = vals[field_names[index]]
        return update_vals

    @staticmethod
    def update_value_equipment_id(vals):
        set_value = {}
        set_value['equipment_ids'] = \
            [(6, 0, [vals['equipment_id']])]
        set_value['room_id'] = False
        return set_value

    def update_value_room_id(self, vals):
        set_value = {}
        set_value['equipment_ids'] = \
            [(6, 0, self.env['resource.calendar.room'].
              browse(vals['room_id']).instruments_ids.ids)]
        return set_value

    @api.multi
    def get_updated_partners(self, employee_ids):
        partner_ids = []
        employee = self.env['hr.employee']
        for e in employee_ids:
            emp = employee.browse(e)
            if emp.user_id:
                partner_ids.append(emp.user_id.partner_id.id)
        return partner_ids

    def update_value_employee_ids(self, vals):
        set_value = {}
        set_value['partner_ids'] = [(
            6, 0, self.get_updated_partners(
                vals['employee_ids'][0][2]))]
        return set_value

    def get_booked_resources(self):
        res = ''
        if self.is_type_task() and self.is_resource_booked():
            res += self.room_id.name + '<br>' if (
                self.room_id) else self.equipment_id.name + '<br>'
        for attendee in self.get_partners():
            hres = self.is_hr_resource_double_booked(attendee)
            partner_attendee = self.env['res.partner'].browse(attendee)
            if hres and partner_attendee:
                res += partner_attendee.name + '<br>'
        if self.is_activity():
            for child in self.child_ids:
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

    def get_double_booked_resources(self, room_id=None,
                                    equipment_id=None,
                                    employee_ids=None,
                                    date_start=None, date_end=None):

        booked_resources = []
        if not date_end and not date_start:
            date_start = self.date_start
            date_end = self.date_end

        if not room_id:
            room_id = self.room_id.id

        if not equipment_id:
            equipment_id = self.equipment_id.id

        if not employee_ids:
            partner_ids = self.get_partners()
        else:
            partner_ids = self.get_partners(employee_ids)

        if self.room_id:
            overlaps = self.env['calendar.event'].search([
                ('room_id', '=', room_id),
                ('start', '<', date_end),
                ('stop', '>', date_start),
                ('state', '!=', 'cancelled'),
            ])
            overlaps_ids = overlaps.ids
            for overlap_id in overlaps_ids:
                if self.env['calendar.event']\
                        .browse(overlap_id).event_task_id.id == self.id:
                    overlaps_ids.remove(overlap_id)
            if len(overlaps_ids) > 0:
                booked_resources.append(self.env['resource.calendar.room']
                                        .browse(room_id).name)

        overlaps_equipment = self.env['calendar.event'].search([
            ('equipment_ids', 'in', [equipment_id]),
            ('start', '<', date_end),
            ('stop', '>', date_start),
            ('state', '!=', 'cancelled'),
        ])
        overlaps_equipment_ids = overlaps_equipment.ids
        for overlap_equipment_id in overlaps_equipment_ids:
            if self.env['calendar.event']\
                    .browse(overlap_equipment_id)\
                    .event_task_id.id == self.id:
                overlaps_equipment_ids.remove(overlap_equipment_id)
        if len(overlaps_equipment_ids) > 0:
            booked_resources.append(self.env['resource.calendar.instrument']
                                        .browse(equipment_id).name)

        for attendee in partner_ids:
            h_res = self.is_hr_resource_double_booked(attendee)
            partner_attendee = self.env['res.partner'].browse(attendee)
            if h_res and partner_attendee:
                booked_resources.append(partner_attendee.name)

        return booked_resources

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

    @api.multi
    def get_partners(self, employee_ids=None):
        if not employee_ids:
            employees = self.employee_ids
        else:
            employees = self.env['hr.employee']\
                .search([('id', 'in', employee_ids)])
        partners = []
        for e in employees:
            if e.user_id:
                partners.append(e.user_id.partner_id.id)
        return partners

