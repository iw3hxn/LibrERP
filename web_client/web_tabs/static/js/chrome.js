openerp.web_tabs = function(openerp) {

    openerp.web.ActionManager = openerp.web.ActionManager.extend({
            
        null_action: function() {
            this.dialog_stop();
            this.new_tab_panel("OpenERP");
            this._activate_tab();
        },
        ir_actions_act_window: function (action, on_close) {
            var self = this;
            if (_(['base.module.upgrade', 'base.setup.installer'])
                    .contains(action.res_model)) {
                var old_close = on_close;
                on_close = function () {
                    openerp.webclient.do_reload().then(old_close);
                };
            }
            if (action.target === 'new') {
                if (this.dialog == null) {
                    this.dialog = new openerp.web.Dialog(this, { width: '80%' });
                    if(on_close)
                        this.dialog.on_close.add(on_close);
                } else {
                    this.dialog_viewmanager.stop();
                }
                this.dialog.dialog_title = action.name;
                this.dialog_viewmanager = new openerp.web.ViewManagerAction(this, action);
                this.dialog_viewmanager.appendTo(this.dialog.$element);
                this.dialog.open();
            } else  {
                if(action.menu_id) {
                    return this.widget_parent.do_action(action, function () {
                        openerp.webclient.menu.open_menu(action.menu_id);
                    });
                }
                this.dialog_stop();
                if (action.res_model === 'res.users' && action.from_menu === undefined){
                    this.content_stop();
                    this.inner_action = action;
                    this.inner_viewmanager = new openerp.web.ViewManagerAction(this, action);
                    this.inner_viewmanager.appendTo(this.$element);
                } else {
                    this.inner_action = action;
                    this.inner_viewmanager = new openerp.web.ViewManagerAction(this, action);
                    this._rename_tab_id();
                    tab = this.new_tab(action.name);
                    this.inner_viewmanager.appendTo(tab);
                    this._activate_tab()
                }

            }
        },
        new_tab: function(tab_name) {
            this.new_tab_panel(tab_name);
            return $('<div id="' + this.element_id + '"/>').appendTo('#oe_app').addClass("ui-tabs-panel ui-widget-content ui-corner-bottom");
        },
        new_tab_panel: function(tab_name) {
            $('#tab_navigator').children().each(
                function(){
                    $(this).removeClass("ui-tabs-selected ui-state-active");
                }
            );
            $('#oe_app').children('div').each(
                function(){
                    $(this).addClass("ui-tabs-hide");
                }
            );
            $('<li><a href="#' + this.element_id + '">' + tab_name + '</a></li>').appendTo('#tab_navigator').addClass("ui-state-default ui-corner-top ui-tabs-selected ui-state-active");
        },
        _rename_tab_id: function() {  
            this.element_id = _.uniqueId('tab-'); // TODO This method fix bug (or maybe feature :D ) -- all widgets have the same id -- "#widget-15"
            $('#' + this.element_id).addClass("ui-tabs-panel ui-widget-content ui-corner-bottom");
        },
        _activate_tab: function () {
            $('#oe_app').tabs({
                closable: true,
                });
        },
    });

    openerp.web.page.FieldMany2OneReadonly = openerp.web.page.FieldMany2OneReadonly.extend({
        set_value: function (value) {
            value = value || null;
            this.invalid = false;
            var self = this;
            this.value = value;
            self.update_dom();
            self.on_value_changed();
            var real_set_value = function(rval) {
                self.value = rval;
                self.$element.find('a')
                        .unbind('click')
                        .text(rval ? rval[1] : '')
                        .click(function () {
                        self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: self.field.relation,
                            res_id: self.value[0],
                            context: self.build_context(),
                            views: [[false, 'page'], [false, 'form']],
                            target: 'current',
                            name: self.string,
                        });
                        return false;
                        });
            };
            if (value && !(value instanceof Array)) {
                new openerp.web.DataSetStatic(
                        this, this.field.relation, self.build_context())
                    .name_get([value], function(data) {
                        real_set_value(data[0]);
                });
            } else {
                $.async_when().then(function() {real_set_value(value);});
            }
        },
    });

};

// vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
