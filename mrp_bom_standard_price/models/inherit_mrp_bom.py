#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from openerp.osv import osv, fields


class mrp_bom(osv.Model):
    _inherit = 'mrp.bom'

    def _compute_list_price(self, cr, uid, ids, field_name, arg, context=None):
        """ Sets particular method for the selected bom type.
        @param field_name: Name of the field
        @param arg: User defined argument
        @return:  Dictionary of values
        """
        res = dict.fromkeys(ids, False)
        for line in self.browse(cr, uid, ids, context=context):
            date = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
            pricelist_id = 2  # todo listen CORTEM for have better specific
            price = self.pool['product.pricelist'].price_get(cr, uid, [pricelist_id], line.product_id.id, line.product_qty or 1.0, None,
                                                     {'uom': line.product_uom.id, 'date': date})[pricelist_id]

        res[line.id] = price
        return res

    _columns = {
        'property_product_pricelist_purchase': fields.property(
            'product.pricelist',
            type='many2one',
            relation='product.pricelist',
            domain=[('type', '=', 'purchase')],
            string="Purchase Pricelist",
            view_load=True,
            help="This pricelist will be used, instead of the default one, for purchases from the current partner"),
        'list_price': fields.function(_compute_list_price, string='List Price', type='float'),
        'standard_price': fields.related('product_id', 'standard_price',
            type='float', relation='product.product', string='Cost price', readonly=True),
    }

    def onchange_product_id2(self, cr, uid, ids, product_id, name, product_qty, product_uom, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        # if product_id:
        #     prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        #     return {'value': {'name': prod.name, 'product_uom': prod.uom_id.id}}
        date = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        pricelist_id = 2 #todo listen CORTEM for have better specific
        price = self.pool['product.pricelist'].price_get(cr, uid, [pricelist_id], product_id, product_qty or 1.0, None, {'uom': product_uom, 'date': date})[pricelist_id]
        res = super(mrp_bom, self).onchange_product_id(cr, uid, ids, product_id, name, context=context)
        res['value']['list_price'] = price
        return res
