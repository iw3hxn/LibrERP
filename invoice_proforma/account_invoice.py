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
from osv import fields, osv


class account_invoice(osv.Model):

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
#        'subject': fields.text(
#            'Subject', help="Main subject, topic of the activity.",
#            ),
    }

    def action_proforma(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return True
        if isinstance(ids, (int, long)):
            ids = [ids]
        ait_obj = self.pool.get('account.invoice.tax')
        
        for inv in self.browse(cr, uid, ids, context=context):
            #import pdb; pdb.set_trace()
            vals = {
                'state': 'proforma2',
                'proforma_number': self.pool.get('ir.sequence').get(
                    cr, uid, 'account.invoice.proforma',
                    ),
                'date_proforma': inv.date_proforma,
            }

            if not inv.date_proforma:
                vals['date_proforma'] = time.strftime('%Y-%m-%d')
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=context)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)
            self.write(cr, uid, inv.id, vals, context=context)

        return True
        #return self.write(
        #    cr, uid, ids, {'state': 'proforma2'}, context=context)


    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'proforma_number': False,
            'date_proforma': False,
        })
        return super(account_invoice, self).copy(cr, uid, id, default, context)
