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
            /**
             * Show a popup Wizard with a message containing the double booked resources.
             * Two buttons are displayed one for continuing and saving an a second one to cancel
             *
             * @override
             */
            var message = _t('Please Confirm your reservation.<br>The following resources are booked:<br>');
            var self = this;

            if(self.modelName == 'calendar.event' ) {
                if (!record._allDay) {
                    var newDateStart = record._start.add(-self.getSession().getTZOffset(record._start), 'minutes').format("YYYY-MM-DD HH:mm:ss");
                    if (!record._end) {
                        var newDateEnd = newDateStart;
                    } else {
                        var newDateEnd = record._end.add(-self.getSession().getTZOffset(record._end), 'minutes').format("YYYY-MM-DD HH:mm:ss");
                    }
                } else {
                    var newDate = record._start.add(-self.getSession().getTZOffset(record._start), 'minutes').format("YYYY-MM-DD HH:mm:ss");
                    var newDateStart = newDate.split(' ')[0] + " 00:00:00";
                    var newDateEnd = newDate.split(' ')[0] + " 23:59:59";
                }
                self._rpc({
                    model: 'calendar.event',
                    method: 'get_double_booked_resources',
                    args: [record.id, newDateStart, newDateEnd],
                }).then(function (booked_resources) {
                    if(booked_resources.length != 0) {
                        var message = _t('The following resources are booked:<br/>');
                        booked_resources.forEach(function (resource){
                            message = message + resource + '<br/>';
                        });
                        message = message + _t('Do you want to continue?');
                        new Dialog(this, {
                            size: 'large',
                            title : _t("Please Confirm your reservation"),
                            $content: $('<div>', {
                                html: message,
                            }),
                            buttons: [
                                {text: _t('Continue'), classes : "btn-primary", click: function() {
                                    self.model.updateRecord(record).always(self.reload.bind(self));
                                }, close:true},
                                {text: _t("Cancel"), click: function() {
                                    self.reload();
                                },close: true}
                            ],
                        }).open();
                    } else {
                        self.model.updateRecord(record).always(self.reload.bind(self));
                    }
                });
            }
            else if (self.modelName == 'project.task') {
                self._rpc({
                    model: 'project.task',
                    method: 'get_double_booked_resources',
                    args: [record.id,
                           false,
                           false,
                           false,
                           record._start.add(-self.getSession().getTZOffset(record._start), 'minutes').format("YYYY-MM-DD HH:mm:ss"),
                           record._end.add(-self.getSession().getTZOffset(record._end), 'minutes').format("YYYY-MM-DD HH:mm:ss"),
                          ],
                }).then(function (booked_resources) {
                    if(booked_resources.length != 0) {

                        var message = _t('The following resources are booked:<br/>');
                        booked_resources.forEach(function (resource){
                            message = message + resource + '<br/>';
                        });
                        message = message + _t('Do you want to continue?');
                        new Dialog(this, {
                            size: 'large',
                            title : _t("Please Confirm your reservation"),
                            $content: $('<div>', {
                                html: message,
                            }),
                            buttons: [
                                {text: _t('Continue'), classes : "btn-primary", click: function() {
                                    self.model.updateRecord(record).always(self.reload.bind(self));
                                }, close:true},
                                {text: _t("Cancel"), click: function() {
                                    self.reload();
                                },close: true}
                            ],
                        }).open();
                    } else {
                        self.model.updateRecord(record).always(self.reload.bind(self));
                    }
                });
            }
        },
    });
});
