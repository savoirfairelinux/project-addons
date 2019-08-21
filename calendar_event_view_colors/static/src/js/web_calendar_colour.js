odoo.define('calendar_event_view_colors.calendar_colour', function (require) {
    "use strict";

    var CalendarView = require('web.CalendarView');
    var CalendarModel = require('web.CalendarModel');
    var CalendarRenderer = require('web.CalendarRenderer');
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

    var CalendarColourRenderer = CalendarRenderer.extend({
        _renderEvents: function () {
                this.$calendar.fullCalendar('removeEvents');
                this.$calendar.fullCalendar('addEventSource', this.state.data);
        },
    });


    var CalendarColourModel = CalendarModel.extend({
        load: function(params){

            var self = this;

            this.modelName = params.modelName;
            this.fields = params.fields;

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
            var color_fields = rpc.query({
                model: 'calendar.color.tag.fields',
                method: 'get_calendar_color_fields',
                args: [params.modelName],
                });
            return color_fields.then(function(calendar_fields){
                self.fieldNames = params.fieldNames.concat(calendar_fields[2])
                                    .concat(calendar_fields[0])
                                    .concat(calendar_fields[1])
                return self.preload_def.then(self._loadCalendar.bind(self));
            }
            );
        },

        _loadColors: function (element, events) {

            var self= this;
            var color_fields = rpc.query({
                model: 'calendar.color.tag.fields',
                method: 'get_calendar_color_fields',
                args: [self.modelName],
            });
            return color_fields.then(function(calendar_fields){
                if (self.fieldColor) {
                    var fieldName = self.fieldColor;
                    _.each(events, function (event) {
                        var value = event.record[fieldName];
                        //if calendar_fields
                        if (calendar_fields[0] != ''){
                            // var my_color = rpc.query({model:self.modelName, method:'get_calendar_tags_values'})
                            event.color_index = event.record[calendar_fields[0]];
                            event.color = event.record[calendar_fields[0]];
                        }
                        //TODO else (if there is no calendar color tag fields
                        else{
                            event.color_index = _.isArray(value) ? value[0] : value;
                        }

                        if(typeof event.record[calendar_fields[2]] != 'undefined' && event.record[calendar_fields[2]] === 'draft') {
                            event.className = 'calendar_hatched_background';
                        }

                        if(event.record[calendar_fields[1]] === 'black'){
                            event.textColor = 'black';
                        }
                        else{
                            event.textColor = 'white';
                        }

                    });
                    self.model_color = self.fields[fieldName].relation || element.model;
                }

                return $.Deferred().resolve();

            });
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
                Renderer: CalendarColourRenderer,
                Controller: CalendarController,
        }),
    });

    viewRegistry.add('calendar_colour', WebCalendarColourView);

});
