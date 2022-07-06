# -*- coding: utf-8 -*-

from openerp.osv import orm, fields


class FullOrderRequirementLineByCategory(orm.TransientModel):

    _name = 'full.order.requirement.line.by.category'
    _rec_name = 'order_requirement_id'

    _columns = {
        'order_requirement_id': fields.many2one('order.requirement', string='Order Requirement', required=False),
        'categ_id': fields.many2one('product.category', string='Category', required=False),
    }

    def open_full_order_requirement(self, cr, uid, ids, context):
        wizard = self.browse(cr, uid, ids, context)[0]

        mod_model = self.pool['ir.model.data']
        act_model = self.pool['ir.actions.act_window']
        action_id = mod_model.get_object_reference(cr, uid, 'sale_order_requirement', 'action_view_full_order_requirement_line')
        action_res = action_id and action_id[1]
        action = act_model.read(cr, uid, action_res, [], context)
        # [['order_requirement_id', '=', 380], ['categ_id', 'child_of', 228]]
        domain = []
        if wizard.order_requirement_id:
            domain.append(('order_requirement_id', '=', wizard.order_requirement_id.id))
        if wizard.categ_id:
            domain.append(('categ_id', 'child_of', wizard.categ_id.id))
        action.update({
            'domain': domain
        })
        return action
