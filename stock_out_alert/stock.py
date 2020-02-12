# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Stock Out Alert
#    Copyright (C) 2013 Enterprise Objects Consulting
#                       http://www.eoconsulting.com.ar
#    Authors: Mariano Ruiz <mrsarm@gmail.com>
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

from openerp.osv import osv
from openerp import pooler
from openerp import tools
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class stock_move(osv.osv):
    _inherit = "stock.move"

    def run_check_op_stock_availability(self, cr, uid, use_new_cursor=False, context={}):
        """
        Runs through scheduler.
        @param use_new_cursor: False or the dbname
        """
        if context is None:
            context = {}
        try:
            if use_new_cursor:
                cr = pooler.get_db(use_new_cursor).cursor()
            _logger.info("Starting products availability check...")
            prod_list = self._check_op_stock_availability(cr, uid, context)
            if len(prod_list) > 0:
                _logger.info("...%s products out of stock found." % len(prod_list))
                mail_message_obj = self.pool['mail.message']
                user_obj = self.pool['res.users']
                group_obj = self.pool['res.groups']
                email_body = self.make_stock_out_email(cr, uid, prod_list, context)
                if _logger.isEnabledFor(logging.DEBUG):
                    _logger.debug("\n" + email_body)
                email_from = tools.config.get('email_from', False)
                if not email_from:
                    email_from = str(user_obj.browse(cr, uid, uid, context=context).user_email)
                wm_monitor_id = group_obj.search(cr, uid, [('name', '=', 'Stock Monitor'), ('category_id.name', '=', 'Warehouse Management')],
                                                 context=context)[0]
                email_to = [str(u.user_email) for u in group_obj.browse(cr, uid, wm_monitor_id, context=context).users]
                mail_message_obj.schedule_with_attach(cr, uid,
                                                      email_from,
                                                      email_to,
                                                      "ERP - " + str(len(prod_list)) + " " + _("products out of stock found"),
                                                      email_body,
                                                      attachments=None,
                                                      subtype='plain',
                                                      reply_to=email_from,
                                                      auto_delete=False,
                                                      context=context)
            else:
                _logger.info("...no product out of stock found.")
            if use_new_cursor:
                cr.commit()
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass

    def _check_op_stock_availability(self, cr, uid, context={}):
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        uom_obj = self.pool.get('product.uom')
        prod_list = []
        orderpoint_ids = orderpoint_obj.search(cr, uid, [('active', '=', True)], context=context)
        for op in orderpoint_obj.browse(cr, uid, orderpoint_ids, context=context):
            product = op.product_id
            uom = product.product_tmpl_id.uom_id
            uom_po = product.product_tmpl_id.uom_po_id
            product_min_qty = uom_obj._compute_qty(cr, uid, op.product_uom.id, op.product_min_qty, uom.id)
            qty = product_min_qty - product.virtual_available
            if qty > 0:
                prod = {}
                prod['uom'] = uom_po
                prod['qty'] = uom_obj._compute_qty(cr, uid, uom.id, qty, uom_po.id)
                prod['product'] = product
                prod['location'] = op.location_id
                prod['company'] = op.company_id
                prod_list.append(prod)
        return prod_list

    def _get_stock_out(self, cr, uid, prod_list, context={}):
        """
        Return a dict with the stock out information,
        grouped by company and location. Ex:
            {
                1: {
                    "company": browse_record(res.company),
                    "locations": {
                        1: {
                            "location": browse_record(stock.location),
                            "products": [
                                {
                                    "product": browse_record(product.product),
                                    "qty": 3,
                                    "uom": browse_record(product.uom),
                                    "origin": "PO/0009"
                                },
                                {
                                ...
                                },
                                ...
                            ],
                        }
                    }
                }
            }
        """
        res = {}
        for p in prod_list:
            location = p['location']
            company = p['company']
            if company.id not in res:
                res[company.id] = {'company': company, 'locations': {}}
            if location.id not in res[company.id]['locations']:
                res[company.id]['locations'][location.id] = {'location': location, 'products': []}
            res_prod = {
                'product': p['product'],
                'qty': p['qty'],
                'uom': p['uom'],
                'origin': p['origin'] if 'origin' in p and p['origin'] else '',
            }
            res[company.id]['locations'][location.id]['products'].append(res_prod)
        return res

    def _get_email_body(self, cr, uid, stock_out, context={}):
        body = "=== " + _("Product List - Out of Stock") + " ==="
        if len(stock_out) == 0:
            body += "\n\n  * %s" % _("No product out of stock found.")
            return body
        head = "  " + _("Product").ljust(38) + _("Qty. Available").rjust(15) + "\t" + _("Qty. Virtual").rjust(
            15) + "\t" + _("Qty. Needed").rjust(15) + "\t" + _("PO").rjust(15) + "\n"
        head += "  " + ("-" * len(_("Product"))).ljust(38) + "-" * 15 + "\t" + "-" * 15 + "\t" + "-" * 15 + "\n"
        for company_id in stock_out.keys():
            body += "\n\n> " + stock_out[company_id]['company'].name + "\n"
            body += "  " + "-" * len(stock_out[company_id]['company'].name)
            for location_id in stock_out[company_id]['locations'].keys():
                location_data = stock_out[company_id]['locations'][location_id]
                body += "\n\n* " + location_data['location'].name + "\n"
                body += "  " + "=" * len(location_data['location'].name) + "\n\n"
                body += head
                if len(location_data['products']) == 0:
                    body += "  %s" % _("No product out of stock found.")
                else:
	            for product_data in location_data['products']:
        		purchase_order = '-' if (product_data['product'].last_purchase_order_id.state == 'done' or not product_data['product'].last_purchase_order_id) else product_data['product'].last_purchase_order_id.name
                    	product_reg = {
				'name': ("[%s] %s" % (product_data['product'].default_code, product_data['product'].name))[0:37],
                        	'qty_available': "%s %s" % (product_data['product'].qty_available, product_data['product'].product_tmpl_id.uom_id.name),
                        	'virtual_available': "%s %s" % (product_data['product'].virtual_available,
                                                        product_data['product'].product_tmpl_id.uom_id.name),
                        	'needed': "%s %s" % (product_data['qty'], product_data['uom'].name),
                        	'purchase_order': purchase_order

                    	}
                    	body += "  %(name)-38s%(qty_available)15s\t%(virtual_available)15s\t%(needed)15s\t%(purchase_order)10s\n" % product_reg
        return body

    def make_stock_out_email(self, cr, uid, prod_list, context={}):
        """
        Make email from procurement
        @return: Mail text
        """
        res = self._get_stock_out(cr, uid, prod_list, context)
        mail = self._get_email_body(cr, uid, res, context)
        return mail

