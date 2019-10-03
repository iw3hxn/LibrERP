# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Micronaet SRL (<http://www.micronaet.it>).
#    Copyright (C) 2014 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time

from openerp.osv import orm
from tools.translate import _


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def action_move_create(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        ait_obj = self.pool['account.invoice.tax']
        amount_tax = 0.0
        if isinstance(ids, (int, long)):
            ids = [ids]
        for inv in self.browse(cr, uid, ids, context=context):
            amount_tax = context.get('amount_tax', 0.0)
            if not amount_tax:
                compute_taxes = ait_obj.compute(cr, uid, inv.id, context=context)
                for tax in compute_taxes:
                    amount_tax += compute_taxes[tax]['amount']

            context.update({'amount_tax': amount_tax})
            super(account_invoice, self).action_move_create(cr, uid, [inv.id], context=context)
        return True

    def onchange_payment_term_date_invoice(self, cr, uid, ids, payment_term_id, date_invoice):
        res = {'value': {}}

        if not ids:
            return res

        if not payment_term_id:
            return res
        context = self.pool['res.users'].context_get(cr, uid)
        pt_obj = self.pool['account.payment.term']
        ait_obj = self.pool['account.invoice.tax']

        if not date_invoice:
            date_invoice = time.strftime('%Y-%m-%d')

        compute_taxes = ait_obj.compute(cr, uid, ids, context=context)
        amount_tax = 0
        for tax in compute_taxes:
            amount_tax += compute_taxes[tax]['amount']
        context.update({'amount_tax': amount_tax})

        pterm_list = pt_obj.compute(cr, uid, payment_term_id, value=1, date_ref=date_invoice, context=context)

        if pterm_list:
            pterm_list = [line[0] for line in pterm_list]
            pterm_list.sort()
            res = {'value': {'date_due': pterm_list[-1]}}
        else:
            payment = self.pool['account.payment.term'].browse(cr, uid, payment_term_id, context)
            raise orm.except_orm(_('Data Insufficient "{0}" !'.format(payment.name)),
                                 _('The payment term of supplier does not have a payment term line!'))
        return res
