# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
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
from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


class account_invoice(orm.Model):

    _inherit = 'account.invoice'

    _columns = {
        'proforma_number': fields.char(
            'Proforma Number',
            size=32,
            readonly=True, help="Proforma Invoice Number",
            ),
        'date_proforma': fields.date(
            'Proforma Date',
            readonly=True,
            states={'draft': [('readonly', False)]},
            select=True, help="Keep empty to use the current date",
            ),
        'date_invoice': fields.date('Invoice Date', readonly=True, states={'draft': [('readonly', False)], 'proforma2': [('readonly', False)]}, select=True,
                                    help="Keep empty to use the current date"),
    }

    def action_proforma(self, cr, uid, ids, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if not ids:
            return True
        if isinstance(ids, (int, long)):
            ids = [ids]
        ait_obj = self.pool['account.invoice.tax']
        
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.number:
                raise orm.except_orm(_("Invoice"),
                                     _("Invoice just validate with number {number}, impossible to Create PROFORMA".format(number=invoice.number)))
            elif invoice.internal_number:
                raise orm.except_orm(_("Invoice"),
                                     _("Invoice just validate with internal number {number}, impossible to Create PROFORMA".format(number=invoice.internal_number)))

            vals = {
                'state': 'proforma2',
                'proforma_number': self.pool['ir.sequence'].get(
                    cr, uid, 'account.invoice.proforma',
                    ),
                'date_proforma': invoice.date_proforma or time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                # 'number': False,
                # 'date_invoice': False,
                # 'internal_number': False
            }
            compute_taxes = ait_obj.compute(cr, uid, invoice.id, context=context)
            self.check_tax_lines(cr, uid, invoice, compute_taxes, ait_obj)
            self.write(cr, uid, invoice.id, vals, context=context)

        return True

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        default = default or {}
        default.update({
            'proforma_number': False,
            'date_proforma': False,
        })
        return super(account_invoice, self).copy(cr, uid, id, default, context)
