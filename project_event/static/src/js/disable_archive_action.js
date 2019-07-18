odoo.define('test_modulo.BasicView', function (require) {
    "use strict";
    
    var session = require('web.session');
    var BasicView = require('web.BasicView');
    BasicView.include({
            init: function(viewInfo, params) {
                var self = this;
                this._super.apply(this, arguments);
                var model = self.controllerParams.modelName in ['res.partner','project.task'] ? 'True' : 'False';
                if(model) {
                    session.user_has_group('project_event.group_project_event_manager').then(function(has_group) {
                        if(!has_group) {
                            self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
                        }
                    });
                }
            },
    });
    });
