# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################


from openerp import SUPERUSER_ID
from openerp.osv import orm, fields
from tools.translate import _


class mass_object(orm.Model):
    _name = "mass.object"

    _columns = {
        'name': fields.char("Name", size=64, required=True, select=1),
        'model_id': fields.many2one('ir.model', 'Model', required=True, select=1),
        'field_ids': fields.many2many('ir.model.fields', 'mass_field_rel', 'mass_id', 'field_id', 'Fields'),
        'ref_ir_act_window': fields.many2one('ir.actions.act_window', 'Sidebar action', readonly=True,
                                            help="Sidebar action to make this template available on records "
                                                 "of the related document model"),
        'ref_ir_value': fields.many2one('ir.values', 'Sidebar button', readonly=True,
                                       help="Sidebar button to open the sidebar action"),
        'model_ids': fields.many2many('ir.model', string='Model List'),
        'group_id': fields.many2many('res.groups', string='Group'),
    }

    def onchange_model(self, cr, uid, ids, model_id, context=None):
        model_ids = []
        if model_id:
            model_obj = self.pool['ir.model']
            model_data = model_obj.browse(cr, uid, model_id, context)
            model_ids = [model_id]
            active_model_obj = self.pool[model_data.model]
            if active_model_obj._inherits:
                for key, val in active_model_obj._inherits.items():
                    found_model_ids = model_obj.search(cr, uid, [('model', '=', key)])
                    if found_model_ids:
                        model_ids.append(found_model_ids[0])

        return {'value': {'model_ids': [(6, 0, model_ids)]}}

    def create_action(self, cr, uid, ids, context=None):
        vals = {}
        action_obj = self.pool['ir.actions.act_window']
        data_obj = self.pool['ir.model.data']
        uid = SUPERUSER_ID
        for data in self.browse(cr, uid, ids, context=context):
            src_obj = data.model_id.model
            button_name = _(u'Mass Editing ({name})'.format(name=data.name))
            vals['ref_ir_act_window'] = action_obj.create(cr, uid, {
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'mass.editing.wizard',
                'src_model': src_obj,
                'view_type': 'form',
                'context': "{'mass_editing_object' : %d}" % data.id,
                'view_mode': 'form,tree',
                'target': 'new',
                'auto_refresh': 1,
                'groups_id': [[6, 0, [group.id for group in data.group_id]]],
            }, context)
            vals['ref_ir_value'] = self.pool['ir.values'].create(cr, uid, {
                'name': button_name,
                'model': src_obj,
                'key2': 'client_action_multi',
                'value': "ir.actions.act_window," + str(vals['ref_ir_act_window']),
                'object': True,
            }, context)
        self.write(cr, uid, ids, {
            'ref_ir_act_window': vals.get('ref_ir_act_window', False),
            'ref_ir_value': vals.get('ref_ir_value', False),
        }, context)
        return True

    def unlink_action(self, cr, uid, ids, context=None):
        uid = SUPERUSER_ID
        for template in self.browse(cr, uid, ids, context=context):
            try:
                if template.ref_ir_act_window:
                    self.pool['ir.actions.act_window'].unlink(cr, uid, template.ref_ir_act_window.id, context)
                if template.ref_ir_value:
                    ir_values_obj = self.pool['ir.values']
                    ir_values_obj.unlink(cr, uid, template.ref_ir_value.id, context)
            except:
                raise orm.except_orm(_("Warning"), _("Deletion of the action record failed."))
        return True

    def unlink(self, cr, uid, ids, context):
        self.unlink_action(cr, uid, ids, context=None)
        super(mass_object, self).unlink(cr, uid, ids, context=context)
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
