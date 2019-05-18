# -*- coding: utf-8 -*-
#    Copyright (C) 2011-12 Domsense s.r.l. <http://www.domsense.com>.
#    Copyright (C) 2012-15 Agile Business Group sagl <http://www.agilebg.com>
#    Copyright (C) 2013-15 LinkIt Spa <http://http://www.linkgroup.it>
#    Copyright (C) 2013-18 Associazione Odoo Italia
#                          <http://www.odoo-italia.org>
#    Copyright (C) 2017    Didotech srl <http://www.didotech.com>
#    Copyright (C) 2017-18 SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import orm, fields
from tools.translate import _


class RemovePeriod(orm.TransientModel):

    def _get_period_ids(self, cr, uid, context=None):
        res = []
        if 'active_id' in context:
            statement_model = self.pool.get('account.vat.period.end.statement')
            statement = statement_model.browse(
                cr, uid, context['active_id'], context)
            type = statement.type
            if type == 'xml':
                for period in statement.period_ids:
                    res.append((period.id, period.name))
                for period in statement.e_period_ids:
                    found = False
                    for item in res:
                        if period.id == item[0]:
                            found = True
                            break
                    if not found:
                        res.append((period.id, period.name))
            elif type == 'xml2':
                for period in statement.e_period_ids:
                    res.append((period.id, period.name))
            elif type == 'month':
                for period in statement.period_ids:
                    res.append((period.id, period.name))
            elif type == 'year':
                for period in statement.y_period_ids:
                    res.append((period.id, period.name))
        return res

    _name = 'remove.period.from.vat.statement'

    _columns = {
        'period_id': fields.selection(
            _get_period_ids, 'Period', required=True),
    }

    def linkable_period(self, cr, uid, ids, context):
        if 'active_id' not in context:
            raise orm.except_orm(_('Error'), _('Current statement not found'))
        # wizard = self.browse(cr, uid, ids, context)[0]
        statement_model = self.pool.get('account.vat.period.end.statement')
        type = statement_model.browse(cr, uid, context['active_id']).type
        field = ''
        field2 = ''
        if type == 'xml':
            field = 'vat_statement_id'
            field2 = 'e_vat_statement_id'
        elif type == 'xml2':
            field = 'e_vat_statement_id'
        elif type == 'month':
            field = 'vat_statement_id'
        elif type == 'year':
            field = 'y_vat_statement_id'
        return field, field2

    def remove_period(self, cr, uid, ids, context=None):
        field, field2 = self.linkable_period(cr, uid, ids, context)
        vals = {field: False}
        if field2:
            vals[field2] = False
        self.pool.get('account.period').write(
            cr, uid, [int(self.browse(cr, uid, ids, context)[0].period_id)],
            vals, context=context)
        self.pool.get('account.vat.period.end.statement').compute_amounts(
            cr, uid, [context['active_id']], context=context)
        return {
            'type': 'ir.actions.act_window_close',
        }
