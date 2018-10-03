# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012 Pexego Sistemas Informáticos (<http://tiny.be>).
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
import logging

from openerp.osv import orm, fields
import decimal_precision as dp

_logger = logging.getLogger(__name__)


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    # def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
    #     if move_line.purchase_line_id:
    #         self.pool['account.invoice.line'].write(cr, uid, [invoice_line_id], {
    #             'discount': move_line.purchase_line_id.discount,
    #             })
    #     return super( stock_picking, self)._invoice_line_hook(cr, uid, move_line, invoice_line_id)

    def _get_price_unit_invoice(self, cursor, user, move_line, type):

        res = super(stock_picking, self)._get_price_unit_invoice(cursor, user, move_line, type)

        if move_line.purchase_line_id:
            res.update({'discount': move_line.purchase_line_id.discount or 0.0, })
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

