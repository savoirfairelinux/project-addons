# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestProjectEventCommon


class TestProjectEventReservation(TestProjectEventCommon):

    def setUp(self):
        super(TestProjectEventReservation, self).setUp()
        self.task_1.parent_id = self.activity_1
        self.task_2.parent_id = self.activity_2

    def test_010_event_action_option(self):
        self.check_event_action_option(self.project_1)

    def test_020_event_action_accept(self):
        self.check_event_action_accept(self.project_1)

    def test_030_action_cancel(self):
        self.do_event_action_option(self.project_1)
        clone_event_ids = self.project_1.task_ids.mapped(
            'child_ids').mapped('reservation_event_id')
        self.check_event_action_cancel(self.project_1)
        tasks = self.project_1.task_ids.mapped('child_ids').mapped(
            'reservation_event_id')
        self.assertEqual(tasks, [0, 0, 0])
        for event_id in clone_event_ids:
            calendar_event = self.env['calendar.event'].browse(
                event_id)
            self.assertEqual(calendar_event.state, 'cancelled')
            self.assertFalse(calendar_event.event_task_id)
        self.do_event_action_option(self.project_1)

    def test_040_action_postpone(self):
        self.do_event_action_accept(self.project_1)
        self.check_event_action_postpone(self.project_1)
        self.check_event_action_accept(self.project_1)

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
            self.assertEqual(
                reservation_event.client_type.id,
                reservation_event.event_task_id.client_type.id)

    def do_event_action_option(self, event):
        res = event.action_option()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_reservation()

    def check_event_action_option(self, event):
        self.do_event_action_option(event)
        self.assertEqual(event.state, 'option')
        self.check_event_childs_state(event, 'option', 'option')
        self.check_event_clone_state(event, 'draft')

    def do_event_action_accept(self, event):
        res = event.action_accept()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_accept_reservation()

    def check_event_action_accept(self, event):
        self.do_event_action_accept(event)
        self.assertEqual(event.state, 'approved')
        self.check_event_childs_state(event, 'approved', 'requested')
        self.check_event_clone_state(event, 'open')

    def check_event_action_cancel(self, event):
        event.action_cancel()
        self.assertEqual(event.state, 'canceled')
        self.check_event_childs_state(event, 'canceled', 'canceled')

    def check_event_action_postpone(self, event):
        event.action_postpone()
        self.assertEqual(event.state, 'postponed')
        self.check_event_childs_state(event, 'postponed', 'postponed')

    def check_event_childs_state(self, event, activity_state, task_state):
        for activity in event.task_ids:
            self.assertEqual(activity.task_state, activity_state)
            for task in activity.child_ids:
                self.assertEqual(task.task_state, task_state)

    def check_event_clone_state(self, event, state):
        event_ids = event.task_ids.mapped(
            'child_ids').mapped('reservation_event_id')
        for event_id in event_ids:
            reservation_event = self.env['calendar.event'].browse(
                event_id)
            self.assertEqual(reservation_event.state, state)
