# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-2015 Didotech srl (<http://www.didotech.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class sale_advance_payment_inv(orm.TransientModel):

    _inherit = "sale.advance.payment.inv"

    def _prepare_advance_invoice_vals(self, cr, uid, ids, context=None):
        """
        extending private method which prepares invoice values
        adding cup end cig
        """
        sale_ids = context.get('active_ids', [])
        result = super(sale_advance_payment_inv, self)._prepare_advance_invoice_vals(cr, uid, ids, context=context)
        sale_obj = self.pool.get('sale.order')
        sale_num = result[0][0]
        inv_dict = result[0][1]
        # put cig and cup values when invoice is created
        for sale in sale_obj.browse(cr, uid, sale_ids, context=context):
            if sale.cig:
                if 'cig' not in inv_dict:
                    inv_dict['cig'] = sale.cig
            if sale.cup:
                if 'cup' not in inv_dict:
                    inv_dict['cup'] = sale.cup
        return [(sale_num, inv_dict)]

