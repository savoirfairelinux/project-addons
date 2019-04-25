/*
    © 2018 Savoir-faire Linux <https://savoirfairelinux.com>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).
*/


odoo.define('project_resource_calendar.event_overlap', function (require) {
"use strict";

    var rpc = require('web.rpc');
    var AbstractRenderer = require('web.AbstractRenderer');
    var core = require('web.core');

    var _t = core._t;

    /* Override fullCalendar configuration */
    var Thread = AbstractRenderer.include({

        start: function () {
            this._super.apply(this, arguments);

            var self = this;

            this.$calendar = this.$(".o_calendar_widget");

            //Documentation here : http://arshaw.com/fullcalendar/docs/
            if(this.$calendar.fullCalendar != null){
                   var fc_options = $.extend({}, this.state.fc_options, {
                        eventOverlap: function(stillEvent, movingEvent) {
                        if(self.model == 'calendar.event'){

                            if(movingEvent.record["start"]._d < Date.now() || movingEvent.record["state"] == "cancelled"){
                                return true;
                            }
                            if(typeof stillEvent.record["room_id"][0] != 'undefined' && typeof movingEvent.record["room_id"][0] != 'undefined'){
                                if(stillEvent.record["room_id"][0] == movingEvent.record["room_id"][0] && stillEvent.record["allow_double_book"] == false){
                                    return false;
                                }
                            }
                            if(typeof stillEvent.record["non_bookable_equipment_ids"] != 'undefined' && typeof movingEvent.record["non_bookable_equipment_ids"] != 'undefined'){
                                var overlap = true;

                                stillEvent.record["non_bookable_equipment_ids"].forEach(function (equipmentStill){
                                   movingEvent.record["non_bookable_equipment_ids"].forEach(function (equipmentMoving){
                                        if(equipmentStill == equipmentMoving) {
                                            overlap = false;
                                            return false;
                                        }
                                   });
                                });
                                return overlap;
                            }
                        }
                        return true;
                    }
                });

                //this.$calendar.fullCalendar('destroy');
                this.$calendar.fullCalendar(fc_options);
                return this._super();
            }
        },
    });

});
