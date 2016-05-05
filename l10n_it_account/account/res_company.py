##############################################################################
#
#    Author: Didotech SRL
#    Copyright 2014 Didotech SRL
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

from openerp.osv import orm, fields


class res_company(orm.Model):

    _inherit = 'res.company'

    _columns = {
        'disable_voucher_onchange_amount': fields.boolean('Disable Automatic Reconciliation in Voucher'),
        'check_invoice_fiscal_position': fields.boolean('Check Fiscal Position on Invoice'),
        'check_invoice_payment_term': fields.boolean('Check Payment Term on Invoice'),
        'stop_invoice_internal_number': fields.boolean('Stop Invoice Validation if invoice with Internal Number'),
    }

    _defaults = {
        'disable_voucher_onchange_amount': True,
    }
