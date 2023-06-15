# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def _compute_purchase_order_list(self, cr, uid, ids, field_name, arg, context):
        def _get_order(x):
            if x.purchase_order_id:
                purchase_order_list.append(x.purchase_order_id.name_get()[0][1])

        res = {}
        for line in self.browse(cr, uid, ids, context):
            purchase_order_list = []
            for order_requirement_line in line.order_requirement_line_ids:
                _get_order(order_requirement_line)
                for bom_line in order_requirement_line.temp_mrp_bom_ids:
                    _get_order(bom_line)

            res[line.id] = ','.join(list(set(purchase_order_list))) if purchase_order_list else ''
        return res

    _columns = {
        # 'order_requirement_line_id': fields.many2one('order.requirement.line', string='Order requirement line', select=True),
        'order_requirement_line_ids': fields.one2many('order.requirement.line', 'sale_order_line_id', string='Order requirement lines'),
        'purchase_order_list': fields.function(_compute_purchase_order_list, type='char', string='Purchase Order')
    }

    def copy(self, cr, uid, ids, default=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        default = default or {}
        default.update({
            'order_requirement_line_ids': []
        })
        return super(SaleOrderLine, self).copy(cr, uid, ids, default, context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'order_requirement_line_ids': []
        })
        return super(SaleOrderLine, self).copy_data(cr, uid, id, default, context=context)

    # TODO: If needed, change the view and attach the button from sale_order_line <==> order_requirement_line
    # def action_open_order_requirement(self, cr, uid, ids, context=None):
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     line = self.browse(cr, uid, ids, context)[0]
    #
    #     view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'sale_order_requirement',
    #                                                            'view_order_requirement_line_form')
    #     view_id = view and view[1] or False
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Product BOM'),
    #         'res_model': 'order.requirement.line',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'view_id': [view_id],
    #         'target': 'new',
    #         'context': {'view_bom': True},
    #         'res_id': line.id
    #     }


