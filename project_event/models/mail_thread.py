# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _


class MailThread(models.AbstractModel):
    _name = 'mail.thread'
    _inherit = ['mail.thread']

    @api.multi
    def _message_track(self, tracked_fields, initial):
        """ For a given record, fields to check (tuple column name, column info)
        and initial values, return a structure that is a tuple containing :

         - a set of updated column names
         - a list of changes
                    (initial value, new value, column name, column info) """
        self.ensure_one()
        changes = set()
        displays = set()
        tracking_value_ids = []
        display_values_ids = []
        TrackingValue = self.env['mail.tracking.value']
        # generate tracked_values data structure: {'col_name': {col_info,
        # new_value, old_value}}
        for col_name, col_info in tracked_fields.items():
            track_visibility = getattr(
                self._fields[col_name],
                'track_visibility',
                'onchange')
            initial_value = initial[col_name]
            new_value = getattr(self, col_name)

            if col_name == 'notes':
                col_info['string'] = _('Note')
                if new_value != initial_value:
                    new_value = _('created/modified')

            if new_value != initial_value and (
                    new_value or initial_value):
                tracking = TrackingValue.create_tracking_values(
                    initial_value, new_value, col_name, col_info)
                if tracking:
                    tracking_value_ids.append([0, 0, tracking])

                if col_name in tracked_fields:
                    changes.add(col_name)

            elif (
                new_value == initial_value and
                track_visibility == 'always' and
                col_name in tracked_fields
            ):
                tracking = TrackingValue.create_tracking_values(
                    initial_value, initial_value, col_name, col_info)
                if tracking:
                    display_values_ids.append([0, 0, tracking])
                    displays.add(col_name)

        if changes and displays:
            tracking_value_ids = display_values_ids + tracking_value_ids

        return changes, tracking_value_ids
