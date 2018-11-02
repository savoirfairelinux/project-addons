odoo.define('project_event.calendar_colour', function (require) {
    "use strict";

    var CalendarView = require('web.CalendarView');
    var CalendarModel = require('web.CalendarModel');
    var CalendarRenderer = require('web.CalendarRenderer');
    var CalendarController = require('web.CalendarController');
    var viewRegistry = require('web.view_registry');
    var rpc = require('web.rpc');

    rpc.query({
        model: "project.task",
        method: "search_read",
        args: [[['activity_task_type', '=', 'task']]],
    }).then(function(listOfEvents) {

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

                            _.each(listOfEvents, function (task) {
                                if(task.id === event.id && task.task_state === 'option' ) {
                                    event.className = 'calendar_hatched_background';
                                    event.textColor = 'black';
                                }
                            });
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

});
