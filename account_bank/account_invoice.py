# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'bank_riba_id': fields.many2one('res.bank', 'Bank for ri.ba.'),
    }

    def onchange_partner_id(self, cr, uid, ids, i_type, partner_id, date_invoice=False, payment_term=False, bank_riba_id=False, company_id=False, context=None):
        result = super(account_invoice, self).onchange_partner_id(
            cr, uid, ids, i_type, partner_id, date_invoice, payment_term, bank_riba_id, company_id)
        
        partner = self.pool['res.partner'].browse(cr, uid, partner_id, context)
        if partner.bank_riba_id:
            result['value']['bank_riba_id'] = partner.bank_riba_id.id
        return result
