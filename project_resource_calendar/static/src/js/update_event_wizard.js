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
        var message = _t('Please Confirm your reservation.<br>');
        var self = this;

        record.source.events.forEach(function(event) {
            if (event.id != record.id ){
                if(record._start._d > event._start._d && record._start._d < event._end._d || record._end._d > event._start._d && record._end._d < event._end._d){
                    var booked_equipments = [];
                    record.record.double_bookable_equipment_ids.forEach(function(record_equipment){
                        event.record.double_bookable_equipment_ids.forEach(function(event_equipment){
                            if(record_equipment == event_equipment){
                                booked_equipments.push(record_equipment);
                            }
                        });
                    });
                    if(booked_equipments.length > 0){
                        message = message + _t('Equipments ') + booked_equipments + _t(' are already booked:<br> Do you want to continue?');
                        self._rpc({
                            model: 'doublebooking.validation.wiz',
                            method: 'create',
                            args: [{event_id: record.id,
                                    message: message,
                                    start_date: record._start.add(-self.getSession().getTZOffset(record._start), 'minutes'),
                                    end_date: record._end.add(-self.getSession().getTZOffset(record._end), 'minutes'),
                                    r_start_date: record.r_start.add(-self.getSession().getTZOffset(record.r_start), 'minutes'),
                                    r_end_date: record.r_end.add(-self.getSession().getTZOffset(record.r_end), 'minutes')
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
                    }
                    if(typeof record.record.room_id[0] != 'undefined'
                    && record.record.room_id[0] == event.record.room_id[0]
                    ){
                        if(record.record.allow_room_double_booking == true){
                            message = message + record.record.room_id[1] + _t(' is already booked:<br> Do you want to continue?');
                            self._rpc({
                                model: 'doublebooking.validation.wiz',
                                method: 'create',
                                args: [{event_id: record.id,
                                        message: message,
                                        start_date: record._start.add(-self.getSession().getTZOffset(record._start), 'minutes'),
                                        end_date: record._end.add(-self.getSession().getTZOffset(record._end), 'minutes'),
                                        r_start_date: record.r_start.add(-self.getSession().getTZOffset(record.r_start), 'minutes'),
                                        r_end_date: record.r_end.add(-self.getSession().getTZOffset(record.r_end), 'minutes')
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
                        }
                        return self.reload.bind(self);
                    }
                }
            }
        });
        return self.model.updateRecord(record).always(self.reload.bind(self));
    },
});

});
