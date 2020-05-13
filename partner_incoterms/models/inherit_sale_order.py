# -*- encoding: utf-8 -*-
##############################################################################
#

from openerp.osv import orm, fields


class sale_order(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterm',
                                       states={'confirmed': [('readonly', True)], 'approved': [('readonly', True)],
                                               'done': [('readonly', True)]}),
    }
    
    def onchange_partner_id(self, cr, uid, ids, partner_id):
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, partner_id)
        if partner_id:
            partner = self.pool['res.partner'].browse(cr, uid, partner_id)
            if partner.default_incoterm_id:
                res['value']['incoterm'] = partner.default_incoterm_id.id
        return res

    def _prepare_order_picking(self, cr, uid, order, context=None):
        res = super(sale_order, self)._prepare_order_picking(cr, uid, order, context)
        res.update({
            'incoterm_id': (order.incoterm and order.incoterm.id) or (order.incoterm_id and order.incoterm_id.id) or False,
        })
        return res
