# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
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
#

from openerp.osv import orm


class purchase_order(orm.Model):
    _inherit = "purchase.order"
    _order = 'date_order desc, name desc, id desc'


class sale_order(orm.Model):
    _inherit = "sale.order"
    _order = 'date_order desc, name desc'


class stock_picking(orm.Model):
    _inherit = "stock.picking"
    _order = 'date desc, id desc'


class stock_move(orm.Model):
    _inherit = "stock.move"
    _order = 'date desc, product_id, id'


class account_invoice(orm.Model):
    _inherit = "account.invoice"
    _order = 'date_invoice desc, number desc, id desc'


class product_template(orm.Model):
    _inherit = "product.template"
    _order = 'name desc'


# class product_product(orm.Model):
#     _inherit = "product.product"
#     _order = 'name desc'

