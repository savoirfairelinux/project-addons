# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from datetime import datetime, timedelta
from odoo import fields
from odoo.addons.project_event.tests.common import TestProjectEventCommon


class TestProjectEventReservation(TestProjectEventCommon):

    def setUp(self):
        super(TestProjectEventReservation, self).setUp()
        self.Tasks = self.env['project.task']
        self.Rooms = self.env['project.task']

        self.activity_1 = self.Tasks.create({
            'name': 'Test Activity 1',
            'activity_task_type': 'activity',
            'project_id': self.project_1.id,
            'responsible_id': self.project_1.responsible_id.id,
            'partner_id': self.project_1.partner_id.id,
            'room_id': self.room_1.id,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(
                datetime.today() + timedelta(hours=4)
            ),
            'child_ids': [(0, 0,
              {
                  'name': 'Test Task Activity 1',
                  'activity_task_type': 'task',
                  'responsible_id': self.project_1.responsible_id.id,
                  'partner_id': self.project_1.partner_id.id,
                  'room_id': self.room_1.id,
                  'date_start': fields.Datetime.to_string(datetime.today()),
                  'date_end': fields.Datetime.to_string(
                      datetime.today() + timedelta(hours=4)
                  ),
              })],
        })

        self.activity_2 = self.Tasks.create({
            'name': 'Test Activity 2',
            'activity_task_type': 'activity',
            'project_id': self.project_1.id,
            'responsible_id': self.project_1.responsible_id.id,
            'partner_id': self.project_1.partner_id.id,
            'room_id': self.room_2.id,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(
                datetime.today() + timedelta(hours=4)),
            'child_ids': [(0, 0,
                           {
                               'name': 'Test Task Activity 2',
                               'activity_task_type': 'task',
                               'responsible_id': self.project_1.responsible_id.id,
                               'partner_id': self.project_1.partner_id.id,
                               'room_id': self.room_2.id,
                               'date_start': fields.Datetime.to_string(
                                   datetime.today()),
                               'date_end': fields.Datetime.to_string(
                                   datetime.today() + timedelta(hours=4)
                               ),
                           })],
        })

    def test_010_event_action_option(self):
        res = self.project_1.action_option()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_reservation()
        self.assertEqual(
            self.project_1.state,
            'option')
        for activity in self.project_1.task_ids:
            self.assertEqual(
                activity.task_state,
                'option')
            for task in activity.child_ids:
                self.assertEqual(
                    task.task_state,
                    'option')
        event_ids = self.project_1.task_ids.mapped(
            'child_ids').mapped('reservation_event_id')
        for event_id in event_ids:
            reservation_event = self.env['calendar.event'].browse(
                event_id)
            self.assertEqual(
                reservation_event.state,
                'draft')

    def test_020_event_action_accept(self):
        res = self.project_1.action_accept()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_accept_reservation()
        self.assertEqual(
            self.project_1.state,
            'accepted')
        for activity in self.project_1.task_ids:
            self.assertEqual(
                activity.task_state,
                'accepted')
            for task in activity.child_ids:
                self.assertEqual(
                    task.task_state,
                    'requested')
        event_ids = self.project_1.task_ids.mapped(
            'child_ids').mapped('reservation_event_id')
        for event_id in event_ids:
            reservation_event = self.env['calendar.event'].browse(
                event_id)
            self.assertEqual(
                reservation_event.state,
                'open')

    # def test_030_action_cancel(self):
    #     res = self.project_1.action_accept()
    #     wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
    #     wiz.confirm_accept_reservation()
    #     self.project_1.action_cancel()
    #     self.assertEqual(self.project_1.state, 'canceled')
    #     for activity in self.project_1.task_ids:
    #         self.assertEqual(
    #             activity.task_state,
    #             'canceled')
    #         for task in activity.child_ids:
    #             self.assertEqual(
    #                 task.task_state,
    #                 'canceled')

    # def test_040_action_cancel_from_option_state(self):
    #     res = self.project_1.action_option()
    #     wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
    #     wiz.confirm_reservation()
    #     self.assertEqual(
    #         self.project_1.state,
    #         'option')
    #     self.project_1.action_cancel()
    #     self.assertEqual(self.project_1.state, 'canceled')
    #     for activity in self.project_1.task_ids:
    #         self.assertEqual(
    #             activity.task_state,
    #             'canceled')
    #         for task in activity.child_ids:
    #             self.assertEqual(
    #                 task.task_state,
    #                 'canceled')

    def test_050_action_draft(self):
        self.project_1.action_draft()
        self.assertEqual(self.project_1.state, 'draft')

    def test_060_check_partner_id_calendar_event_as_client_of_task(self):
        res = self.project_1.action_accept()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_accept_reservation()
        event_ids = self.project_1.task_ids.mapped(
            'child_ids').mapped('reservation_event_id')
        for event_id in event_ids:
            reservation_event = self.env['calendar.event'].browse(
                event_id)
            self.assertEqual(
                reservation_event.client_id.id,
                self.project_1.partner_id.id)
