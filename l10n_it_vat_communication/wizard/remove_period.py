# -*- coding: utf-8 -*-
#    Copyright (C) 2017    SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# [2017: SHS-AV s.r.l.] First version
#
from openerp.osv import fields, orm
from openerp.tools.translate import _


class RemovePeriod(orm.TransientModel):

    _name = 'remove.period.from.vat.commitment'

    def _get_period_ids(self, cr, uid, context=None):
        commitment_obj = self.pool['account.vat.communication']
        res = []
        if 'active_id' in context:
            commitment = commitment_obj.browse(
                cr, uid, context['active_id'], context)
            for period in commitment.period_ids:
                res.append((period.id, period.name))
        return res

    _columns = {
        'period_id': fields.selection(
            _get_period_ids, 'Period', required=True),
    }

    def remove_period(self, cr, uid, ids, context=None):
        if 'active_id' not in context:
            raise orm.except_orm(_('Error'), _('Current commitment not found'))
        self.pool['account.period'].write(
            cr, uid, [int(self.browse(cr, uid, ids, context)[0].period_id)],
            {'vat_commitment_id': False}, context=context
        )
        self.pool['account.vat.communication'].compute_amounts(
            cr, uid, [context['active_id']], context=context)
        return {
            'type': 'ir.actions.act_window_close',
        }
