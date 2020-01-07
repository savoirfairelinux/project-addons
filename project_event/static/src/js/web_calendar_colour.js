odoo.define('project_event.calendar_colour', function (require) {
    "use strict";

    var CalendarView = require('web.CalendarView');
    var CalendarModel = require('web.CalendarModel');
    var CalendarController = require('web.CalendarController');
    var viewRegistry = require('web.view_registry');
    var rpc = require('web.rpc');
    var Context = require('web.Context');

    function dateToServer (date) {
        return date.clone().utc().locale('en').format('YYYY-MM-DD HH:mm:ss');
    }

    rpc.query({
             model: 'task.category',
             method: 'get_category_list'
    }).then(function (category_list) {
        var style = document.createElement('style');
        style.type = 'text/css';
        style.innerHTML = '';
        for(var i = 0; i < category_list.length; i++)
        {
            if(category_list[i]["color"] != false){
                style.innerHTML = style.innerHTML + " .o_underline_color_category_"+category_list[i]["id"]+" { border-bottom: 4px solid "+category_list[i]["color"] + "; } ";
            }else {
                style.innerHTML = style.innerHTML + " .o_underline_color_category_"+category_list[i]["id"]+" { border-bottom: 4px solid #3a87ad; } ";
            }
        }
        document.getElementsByTagName('head')[0].appendChild(style);
    });

    var CalendarColourModel = CalendarModel.extend({
        load: function(params){

            var self = this;

            this.modelName = params.modelName;
            this.fields = params.fields;

            switch(params.modelName){
                case 'calendar.event':
                    this.fieldNames = params.fieldNames.concat("state")
                                    .concat("color")
                                    .concat("is_task_event")
                                    .concat("font_color")
                    break;
                case 'project.task':
                    this.fieldNames = params.fieldNames.concat("task_state").concat("color").concat("font_color");
                    break;
                default:
                    this.fieldNames = params.fieldNames;
            }

            this.fieldsInfo = params.fieldsInfo;
            this.mapping = params.mapping;
            this.mode = params.mode;       // one of month, week or day
            this.scales = params.scales;   // one of month, week or day

            // Check whether the date field is editable (i.e. if the events can be
            // dragged and dropped)
            this.editable = params.editable;
            this.creatable = params.creatable;

            // display more button when there are too much event on one day
            this.eventLimit = params.eventLimit;

            // fields to display color, e.g.: user_id.partner_id
            this.fieldColor = params.fieldColor;
            if (!this.preload_def) {
                this.preload_def = $.Deferred();
                $.when(
                    this._rpc({model: this.modelName, method: 'check_access_rights', args: ["write", false]}),
                    this._rpc({model: this.modelName, method: 'check_access_rights', args: ["create", false]}))
                .then(function (write, create) {
                    self.write_right = write;
                    self.create_right = create;
                    self.preload_def.resolve();
                });
            }

            this.data = {
                domain: params.domain,
                context: params.context,
                // get in arch the filter to display in the sidebar and the field to read
                filters: params.filters,
            };

            this.setDate(params.initialDate);
            // Use mode attribute in xml file to specify zoom timeline (day,week,month)
            // by default month.
            this.setScale(params.mode);

            _.each(this.data.filters, function (filter) {
                if (filter.avatar_field && !filter.avatar_model) {
                    filter.avatar_model = self.modelName;
                }
            });

            return this.preload_def.then(this._loadCalendar.bind(this));
        },

        _loadColors: function (element, events) {
                if (this.fieldColor) {
                    var fieldName = this.fieldColor;
                    _.each(events, function (event) {
                        var value = event.record[fieldName];
                        event.color_index = event.record["color"];
                        event.color = event.record["color"];

                        if((typeof event.record["task_state"] != 'undefined' && (event.record["task_state"] === 'option' || event.record["task_state"] === 'draft')) || (typeof event.record["state"] != 'undefined' && event.record["state"] === 'draft')) {
                            event.className = 'calendar_hatched_background';
                        }

                        if(event.record["font_color"] === 'black'){
                                event.textColor = 'black';
                        } else {
                                event.textColor = 'white';
                        }

                        if(event.record['is_task_event'] === true){
                            event.editable = false;
                        }
                    });
                    this.model_color = this.fields[fieldName].relation || element.model;
                }
                return $.Deferred().resolve();
        },
        updateRecord: function (record) {
            // Cannot modify actual name yet
            var data = _.omit(this.calendarEventToRecord(record), 'name');
            for (var k in data) {
                if (data[k] && data[k]._isAMomentObject) {
                    data[k] = dateToServer(data[k]);
                }
            }

            if((typeof record["task_state"] != 'undefined' && record["task_state"] === 'option') || (typeof record["state"] != 'undefined' && record["state"] === 'draft')) {
                record.className = 'calendar_hatched_background';
                record.textColor = 'black';
            }

            var context = new Context(this.data.context, {from_ui: true});
            return this._rpc({
                model: this.modelName,
                method: 'write',
                args: [[record.id], data],
                context: context
            });
        },
    });

    var WebCalendarColourView = CalendarView.extend({
        config: _.extend({}, CalendarView.prototype.config, {
                Model: CalendarColourModel,
                Controller: CalendarController,
        }),
    });

    viewRegistry.add('calendar_colour', WebCalendarColourView);

});
