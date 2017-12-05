# -*- encoding: utf-8 -*-
##############################################################################
#

from openerp.osv import orm, fields


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    _columns = {
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterm',
                                       states={'confirmed': [('readonly', True)], 'approved': [('readonly', True)],
                                               'done': [('readonly', True)]}),
    }
    
    def onchange_partner_id(self, cr, uid, ids, partner_id):
        res = super(purchase_order, self).onchange_partner_id(cr, uid, ids, partner_id)
        if partner_id:
            partner = self.pool['res.partner'].browse(cr, uid, partner_id)
            if partner.default_incoterm_id:
                res['value']['incoterm_id'] = partner.default_incoterm_id.id
        return res

