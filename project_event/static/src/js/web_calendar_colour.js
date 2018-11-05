odoo.define('project_event.calendar_colour', function (require) {
    "use strict";

    var CalendarView = require('web.CalendarView');
    var CalendarModel = require('web.CalendarModel');
    var CalendarRenderer = require('web.CalendarRenderer');
    var CalendarController = require('web.CalendarController');
    var viewRegistry = require('web.view_registry');

    var CalendarColourRenderer = CalendarRenderer.extend({
        /* Je n'ai rien changé ici mais je voulais montrer la methode que fait le
           rendering des evenements du calendrier. Ça va etre utile après.

           https://github.com/odoo/odoo/blob/11.0/addons/web/static/src/js/views/calendar/calendar_renderer.js#L464
        */
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
            this.fieldNames = params.fieldNames.concat("task_state");
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
        /* La logique qu'on cherchait etait dans le model et pas dans le renderer */
        _loadColors: function (element, events) {
                if (this.fieldColor) {
                    var fieldName = this.fieldColor;
                    _.each(events, function (event) {
                        var value = event.record[fieldName];
                        event.color_index = _.isArray(value) ? value[0] : value;
                        /* La librairie fullCalendar s'attend à avoir un champ colour avec
                           la valeur CSS de la couleur mais Odoo utilise un autre champ (color_index)
                           donc ici va juste ignorer le color_index et ajouter le champ colour
                        */
                        event.color = _.isArray(value) ? value[0] : value;

                        if(event.record["task_state"] === 'option' ) {
                            event.className = 'calendar_hatched_background';
                            event.textColor = 'black';
                        }

                        if(event.color === '#FFFFFF'){
                            event.textColor = 'black';
                        }
                    });
                    this.model_color = this.fields[fieldName].relation || element.model;
                }
                return $.Deferred().resolve();
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
