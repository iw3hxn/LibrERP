# -*- coding: utf-8 -*-
#    Copyright (C) 2011-12 Domsense s.r.l. <http://www.domsense.com>.
#    Copyright (C) 2012-15 Agile Business Group sagl <http://www.agilebg.com>
#    Copyright (C) 2013-15 LinkIt Spa <http://http://www.linkgroup.it>
#    Copyright (C) 2013-17 Associazione Odoo Italia
#                          <http://www.odoo-italia.org>
#    Copyright (C) 2017    Didotech srl <http://www.didotech.com>
#    Copyright (C) 2017    SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import orm, fields
from tools.translate import _


class remove_period(orm.TransientModel):

    def _get_period_ids(self, cr, uid, context=None):
        statement_obj = self.pool.get('account.vat.period.end.statement')
        res = []
        if 'active_id' in context:
            statement = statement_obj.browse(
                cr, uid, context['active_id'], context)
            for period in statement.period_ids:
                res.append((period.id, period.name))
        return res

    _name = 'remove.period.from.vat.statement'

    _columns = {
        'period_id': fields.selection(
            _get_period_ids, 'Period', required=True),
    }

    def remove_period(self, cr, uid, ids, context=None):
        if 'active_id' not in context:
            raise orm.except_orm(_('Error'), _('Current statement not found'))
        self.pool.get('account.period').write(
            cr, uid, [int(self.browse(cr, uid, ids, context)[0].period_id)],
            {'vat_statement_id': False}, context=context)
        self.pool.get('account.vat.period.end.statement').compute_amounts(
            cr, uid, [context['active_id']], context=context)
        return {
            'type': 'ir.actions.act_window_close',
        }
