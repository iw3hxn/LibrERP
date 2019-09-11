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


class AddPeriod(orm.TransientModel):

    _name = 'add.period.to.vat.statement'

    _columns = {
        'period_id': fields.many2one(
            'account.period', 'Period', required=True),
    }

    def linkable_period(self, cr, uid, ids, context):
        if 'active_id' not in context:
            raise orm.except_orm(_('Error'), _('Current statement not found'))
        wizard = self.browse(cr, uid, ids, context)[0]
        statement_pool = self.pool.get('account.vat.period.end.statement')
        type = statement_pool.browse(cr, uid, context['active_id']).type
        linked_vat = False
        field = ''
        field2 = ''
        if type == 'xml':
            field = 'vat_statement_id'
            field2 = 'e_vat_statement_id'
            if wizard.period_id.vat_statement_id:
                linked_vat = wizard.period_id.vat_statement_id
            if wizard.period_id.e_vat_statement_id:
                linked_vat = wizard.period_id.e_vat_statement_id
        elif type == 'xml2':
            field = 'e_vat_statement_id'
            # if wizard.period_id.e_vat_statement_id:
            #     linked_vat = wizard.period_id.e_vat_statement_id
        elif type == 'month':
            field = 'vat_statement_id'
            if wizard.period_id.vat_statement_id:
                linked_vat = wizard.period_id.vat_statement_id
        elif type == 'year':
            field = 'y_vat_statement_id'
            if wizard.period_id.y_vat_statement_id:
                linked_vat = wizard.period_id.y_vat_statement_id
        return field, field2, linked_vat

    def add_period(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids, context)[0]
        statement_pool = self.pool.get('account.vat.period.end.statement')
        field, field2, linked_vat = self.linkable_period(cr, uid, ids, context)
        if linked_vat:
            raise orm.except_orm(
                _('Error'),
                _('Period %s is associated to statement %s yet') %
                (wizard.period_id.name,
                 linked_vat.date)
            )
        vals = {field: context['active_id']}
        if field2:
            vals[field2] = context['active_id']
        wizard.period_id.write(vals)
        statement_pool.compute_amounts(
            cr, uid, [context['active_id']], context=context)
        return {
            'type': 'ir.actions.act_window_close',
        }
