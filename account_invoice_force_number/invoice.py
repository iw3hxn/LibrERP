# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class account_invoice(orm.Model):
    _inherit = "account.invoice"
    _columns = {
        'internal_number': fields.char('Invoice Number', size=32, readonly=True,
                                       states={'draft': [('readonly', False)]}),
    }

    def onchange_internal_number(self, cr, uid, ids, internal_number, invoice_type, journal_id, context={}):
        if not internal_number:
            return {'value': {}, 'warning': {}}

        warning = {}
        if invoice_type in ['out_invoice', 'out_refund']:
            invoice_search_ids = self.search(cr, uid, [('type', 'in', ['out_invoice', 'out_refund']), ('number', '=', internal_number)], context=context)
            if invoice_search_ids:
                raise orm.except_orm(_('Invoice'), _('Caution there are another invoice with number {invoice_number}').format(invoice_number=internal_number))
            sequence_id = self.pool['account.journal'].browse(cr, uid, journal_id, context).sequence_id.id
            recovery_ids = self.pool['ir.sequence_recovery'].search(cr, uid, [('name', '=', 'account.invoice'), ('sequence_id', '=', sequence_id)], context=context)
            if recovery_ids:
                recovery_number = []
                for recovery in self.pool['ir.sequence_recovery'].browse(cr, uid, recovery_ids, context):
                    if recovery.sequence != internal_number:
                        recovery_number.append(recovery.sequence)
                if recovery_number:
                    recovery_number = '\n'.join(recovery_number)
                    warning = {
                        'title': _('Recovery Sequence'),
                        'message': _('Warning there are another invoice number to recovery: \n {recovery_number}').format(recovery_number=recovery_number)
                    }
        return {'value': {}, 'warning': warning}
