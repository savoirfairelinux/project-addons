odoo.define('project_resource_calendar.WizardCalendarController', function (require) {
    "use strict";

    /**
     * Calendar Controller
     *
     * This is the controller in the Model-Renderer-Controller architecture of the
     * calendar view.  Its role is to coordinate the data from the calendar model
     * with the renderer, and with the outside world (such as a search view input)
     */

    var CalendarController = require('web.CalendarController');
    var QuickCreate = require('web.CalendarQuickCreate');
    var dialogs = require('web.view_dialogs');
    var Dialog = require('web.Dialog');
    var core = require('web.core');

    var _t = core._t;
    var QWeb = core.qweb;

    CalendarController.include({

        _updateRecord: function (record) {
            var message = _t('Please Confirm your reservation.<br>The following resources are booked:<br>');
            var self = this;

            if(self.modelName == 'calendar.event') {
                self._rpc({
                    model: 'calendar.event',
                    method: 'get_double_booked_resources',
                    args: [record.id,
                           record._start.add(-self.getSession().getTZOffset(record._start), 'minutes'),
                           record._end.add(-self.getSession().getTZOffset(record._start), 'minutes')
                          ],
                }).then(function (booked_resources) {
                    if(booked_resources.length != 0){

                        booked_resources.forEach(function (resource){
                            message = message + resource + '<br/>';
                        });

                        message = message + _t('<br>Do you want to continue?');
                        self._rpc({
                            model: 'doublebooking.validation.wiz',
                            method: 'create',
                            args: [{event_id: record.id,
                                    message: message,
                                    start_date: record._start,
                                    end_date: record._end,
                                    r_start_date: record.r_start.add(-self.getSession().getTZOffset(record._start), 'minutes'),
                                    r_end_date: record.r_end.add(-self.getSession().getTZOffset(record._end), 'minutes'),
                                   }],
                        }).then(function (wizard) {
                            self.do_action({
                                name: 'Confirm double booking reservation',
                                res_model: 'doublebooking.validation.wiz',
                                views: [[false, 'form']],
                                type: 'ir.actions.act_window',
                                view_type: "form",
                                view_mode: "form",
                                target: "new",
                                res_id: wizard,
                            });
                        });
                        return self.reload.bind(self);
                    }else{
                        return self.model.updateRecord(record).always(self.reload.bind(self));
                    }
                });
            }
            else if (self.modelName == 'project.task') {
                self._rpc({
                    model: 'project.task',
                    method: 'get_double_booked_resources',
                    args: [record.id,
                           record._start.add(-self.getSession().getTZOffset(record._start), 'minutes'),
                           record._end.add(-self.getSession().getTZOffset(record._end), 'minutes')
                          ],
                }).then(function (booked_resources) {
                    if(booked_resources.length != 0){

                        booked_resources.forEach(function (resource){
                            message = message + resource + '<br/>';
                        });

                        message = message + _t('<br>Do you want to continue?');
                        self._rpc({
                            model: 'doublebooking.validation.wiz',
                            method: 'create',
                            args: [{task_id: record.id,
                                    message: message,
                                    start_date: record._start,
                                    end_date: record._end,
                                    r_start_date: record.r_start.add(-self.getSession().getTZOffset(record._start), 'minutes'),
                                    r_end_date: record.r_end.add(-self.getSession().getTZOffset(record._end), 'minutes')
                                   }],
                        }).then(function (wizard) {
                            self.do_action({
                                name: 'Confirm double booking reservation',
                                res_model: 'doublebooking.validation.wiz',
                                views: [[false, 'form']],
                                type: 'ir.actions.act_window',
                                view_type: "form",
                                view_mode: "form",
                                target: "new",
                                res_id: wizard,
                            });
                        });
                        return self.reload.bind(self);
                    }else{
                        return self.model.updateRecord(record).always(self.reload.bind(self));
                    }
                });
            }
        },
    });
});
