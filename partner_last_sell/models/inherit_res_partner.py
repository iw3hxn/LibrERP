# -*- encoding: utf-8 -*-
##############################################################################

from openerp.osv import orm, fields


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def _get_work_history(self, cr, uid, ids, prop, unknow_none, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = dict.fromkeys(ids, False)
        order_obj = self.pool['sale.order']
        for partner_id in ids:
            order_ids = order_obj.search(cr, uid, [('partner_id', '=', partner_id), ('state', 'in', ['manual', 'progress', 'done'])], context=context, limit=1)
            if order_ids:
                date_confirm = order_obj.read(cr, uid, order_ids, ['date_confirm'], context)[0]['date_confirm']
                res[partner_id] = date_confirm
        return res

    def _get_partner(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order').browse(cr, uid, ids, context=context):
            if line.state in ['manual', 'progress', 'done']:
                result[line.partner.id] = True
        return result.keys()

    _columns = {
        'date_last_sale': fields.function(_get_work_history, string="Last Sale Activity", type='date', store={
            'sale.order': (_get_partner, ['state'], 10),
        }),
    }
