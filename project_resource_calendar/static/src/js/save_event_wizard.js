odoo.define('project_resource_calendar.WizardFormController', function (require) {
"use strict";

    var FormController = require('web.FormController');
    var core = require('web.core');
    var Dialog = require('web.Dialog');

    var _t = core._t;

    FormController.include({
        /**
         * Show a popup with double booked resources, if user click continue
         * changes are send to backend
         *
         * @override
         */
        _onSave: function (ev) {

            var self = this;
            if(self.modelName == 'calendar.event'){
                if(!self.renderer.state.data.start_datetime && !self.renderer.state.data.allday){
                    this.do_warn(_t('Starting at'), 'is empty');
                    return null;
                }
                if(self.renderer.state.data.duration <= 0 && !self.renderer.state.data.allday){
                    this.do_warn(_t('Duration'), 'is equal to 00:00');
                    return null;
                }
                var equipment_ids  = [];
                self.renderer.state.data.equipment_ids.data.forEach(function(equipment_id){
                    equipment_ids.push(equipment_id.data.id);
                });

                var partner_ids  = [];
                self.renderer.state.data.partner_ids.data.forEach(function(partner_id){
                    partner_ids.push(partner_id.data.id);
                });


                self._rpc({
                    model: 'calendar.event',
                    method: 'get_calendar_booked_resources',
                    args: [
                           self.renderer.state.data.id,
                           self.renderer.state.data.room_id.count == 0 ? self.renderer.state.data.room_id.data.id : false,
                           equipment_ids,
                           partner_ids,
                           self.renderer.state.data.allday ? self.renderer.state.data.start : self.renderer.state.data.start_datetime,
                           self.renderer.state.data.duration,
                           self.renderer.state.data.allday,
                          ],
                }).then(function (booked_resources) {
                    if(booked_resources.length != 0){
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
                                    ev.stopPropagation(); // Prevent x2m lines to be auto-saved
                                    self.saveRecord();
                                }, close:true},
                                {text: _t("Cancel"), close: true}
                            ],
                        }).open();
                    }else{
                        ev.stopPropagation(); // Prevent x2m lines to be auto-saved
                        self.saveRecord();
                    }
                });
            }else if(self.modelName == 'project.task' && self.renderer.state.data.activity_task_type == "task" && self.renderer.state.data.task_state != "draft"){

                if(!self.renderer.state.data.date_start){
                    this.do_warn(_t('Starting at'), 'is empty');
                    return null;
                }
                if(!self.renderer.state.data.date_end){
                    this.do_warn(_t('Ending at'), 'is empty');
                    return null;
                }
                if(self.renderer.state.data.date_end > self.renderer.state.data.start_end){
                    this.do_warn(_t('Ending date > Starting date'), 'Date error');
                    return null;
                }
                var employee_ids  = [];
                self.renderer.state.data.employee_ids.data.forEach(function(employee_id){
                    employee_ids.push(employee_id.data.id);
                });
                self._rpc({
                    model: 'project.task',
                    method: 'get_double_booked_resources',
                    args: [
                           self.renderer.state.data.id,
                           self.renderer.state.data.room_id.count == 0 ? self.renderer.state.data.room_id.data.id : false,
                           self.renderer.state.data.equipment_id.count == 0 ? self.renderer.state.data.equipment_id.data.id : false,
                           employee_ids,
                           self.renderer.state.data.date_start,
                           self.renderer.state.data.date_end
                          ],
                }).then(function (booked_resources) {
                    if(booked_resources.length != 0){
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
                                    ev.stopPropagation(); // Prevent x2m lines to be auto-saved
                                    self.saveRecord();
                                }, close:true},
                                {text: _t("Cancel"), close: true}
                            ],
                        }).open();
                    }else{
                        ev.stopPropagation(); // Prevent x2m lines to be auto-saved
                        self.saveRecord();
                    }
                });
            }else{
                ev.stopPropagation(); // Prevent x2m lines to be auto-saved
                self.saveRecord();
            }
        },
    });
});