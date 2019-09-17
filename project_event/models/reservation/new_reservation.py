from odoo import fields, models, api, _

MSG_RES = 'The following resources are already booked:<br>'
MSG_CONFIRM = 'Please confirm your reservation.<br>'
MSG_CONTINUE = 'Do you want to continue?'

class Reservation(models.TransientModel):
    _name = 'project.newreservation'

    activity_task_type = fields.Selection(
        [
            ('activity', 'Activity'),
            ('task', 'Task'),
        ],
        string='Type',
    )
    reservation_event_id = fields.Integer(
        string='Reservation event',
    )
    date_start = fields.Datetime(
        string='Starting Date',
        default=None,
        index=True,
        copy=False,
    )
    date_end = fields.Datetime(
        string='Ending Date',
        index=True,
        copy=False,
    )
    resource_type = fields.Selection([
        ('user', 'Human'),
        ('equipment', 'Equipment'),
        ('room', 'Room')],
        string='Resource Type',
        default='room',
    )
    employee_ids = fields.Many2many(
        'hr.employee', 'task_emp_rel',
        'task_id', 'employee_id',
        string='Employees'
    )
    client_type = fields.Many2one(
        'res.partner.category.type',
        string='Client Type',
    )
    responsible_id = fields.Many2one(
        'res.partner',
        string='Task/Activity Responsible',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
    )
    sector_id = fields.Many2one(
        'res.partner.sector',
        string='Faculty Sector'
    )
    category_id = fields.Many2one(
        'task.category',
        string='Category'
    )
    room_id = fields.Many2one(
        string='Room',
        comodel_name='resource.calendar.room',
        ondelete='set null',
    )
    equipment_id = fields.Many2one(
        string='Equipment',
        comodel_name='resource.calendar.instrument',
        ondelete='set null',
    )
    complete_name = fields.Char(
        string='Complete Name'
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task',
    )

    @api.multi
    def do_reservation(self):
        self.ensure_one()
        self.do_task_reservation()
        return self.reservation_event_id
    
    def do_task_reservation(self):
        self.draft_resources_reservation()
        #==self.send_message(cuttent_state='draft', 'option')
        
        #===treat====missing
        # if self.task_state not in ['option', 'done']:
        #     self.send_message('option')

    @api.multi
    def draft_resources_reservation(self):
        self.ensure_one()
        if not self.reservation_event_id:
            self.request_reservation()
    
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
            'event_task_id': self.task_id.id,
            'is_task_event': True,
            'sector_id': self.sector_id.id if self.sector_id else None,
            'category_id': self.category_id.id,
            'state': 'draft'
        }
        new_event = calendar_event.create(values)
        self.reservation_event_id = new_event.id
        if self.room_id:
            self.reserve_equipment_inside(new_event.id)

    @api.multi
    def reserve_equipment_inside(self, event_id):
        self.ensure_one()
        calendar_event = self.env['calendar.event'].browse(event_id)
        calendar_event.write(
            {
                'equipment_ids': [(6, 0, self.get_equipment_ids_inside())]
            })

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

    @api.multi
    def get_equipment_ids_inside(self):
        room_id = self.env['resource.calendar.room']. \
            browse(self.room_id).id
        return room_id.instruments_ids.ids
