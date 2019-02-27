# -*- coding: utf-8 -*-

from openerp.osv import fields, orm


class riba_didtinta_line(orm.Model):
    _inherit = "riba.distinta.line"

    def _get_move_lines(self, cr, uid, ids, context=None):
        result = []
        for move in self.pool.get('account.move').browse(cr, uid, ids, context=context):
            for line in move.line_id:
                result.append(line.id)
        return result

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
                                             store={
                                                 'riba.distinta.line': (lambda self, cr, uid, ids, c={}: ids, ['partner_id'], 10),
                                                 'account.invoice': (_get_move_lines, ['move_id'], 10),
                                             }),

    }

