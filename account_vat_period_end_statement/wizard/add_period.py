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


class add_period(orm.TransientModel):

    _name = 'add.period.to.vat.statement'

    _columns = {
        'period_id': fields.many2one(
            'account.period', 'Period', required=True),
    }

    def add_period(self, cr, uid, ids, context=None):
        if 'active_id' not in context:
            raise orm.except_orm(_('Error'), _('Current statement not found'))
        statement_pool = self.pool['account.vat.period.end.statement']
        wizard = self.browse(cr, uid, ids, context)[0]
        if wizard.period_id.vat_statement_id:
            raise orm.except_orm(
                _('Error'), _('Period %s is associated to statement %s yet') %
                (wizard.period_id.name, wizard.period_id.vat_statement_id.date)
            )
        wizard.period_id.write({'vat_statement_id': context['active_id']})
        statement_pool.compute_amounts(
            cr, uid, [context['active_id']], context=context)
        return {
            'type': 'ir.actions.act_window_close',
        }
