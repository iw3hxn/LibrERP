# -*- coding: utf-8 -*-

from openerp.osv import fields, orm


class riba_distinta_line(orm.Model):
    _inherit = "riba.distinta.line"

    def _get_mandate(self, cr, uid, ids, field_name, arg, context=None):
        mandate_pool = self.pool['account.banking.mandate']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = False
            if line.partner_id:
                mandate_ids = mandate_pool.search(cr, uid, [('partner_id', '=', line.partner_id.id), ('state', '=', 'valid')], context=context)
                if mandate_ids:
                    res[line.id] = mandate_ids[0]
        return res

    _columns = {
        'mandate_id': fields.function(_get_mandate, method=True, string="Mandate", type="many2one", relation="account.banking.mandate",
                                      store=False),

    }

