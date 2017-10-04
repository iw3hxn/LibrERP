# -*- coding: utf-8 -*-
#    Copyright (C) 2011-12 Domsense s.r.l. <http://www.domsense.com>.
#    Copyright (C) 2012-15 Agile Business Group sagl <http://www.agilebg.com>
#    Copyright (C) 2013-15 LinkIt Spa <http://http://www.linkgroup.it>
#    Copyright (C) 2013-17 Associazione Odoo Italia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import fields, orm
from openerp.tools.translate import _


class AddPeriod(orm.TransientModel):

    _name = 'add.period.to.vat.commitment'

    _columns = {
        'period_id': fields.many2one(
            'account.period', 'Period', required=True),
    }

    def add_period(self, cr, uid, ids, context=None):
        if 'active_id' not in context:
            raise orm.except_orm(_('Error'), _('Current commitment not found'))

        wizard = self.browse(cr, uid, ids, context)[0]
        if wizard.period_id.vat_commitment_id:
            raise orm.except_orm(
                _('Error'),
                _('Period %s is already associated to commitment') %
                (wizard.period_id.name),
            )
        wizard.period_id.write({'vat_commitment_id': context['active_id']})
        self.pool['account.vat.communication'].compute_amounts(
            cr, uid, [context['active_id']], context=context)

        return {
            'type': 'ir.actions.act_window_close',
        }
