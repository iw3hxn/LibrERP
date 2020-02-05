# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2017 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
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
from openerp.tools.translate import _


class purchase_order(orm.Model):

    _inherit = 'purchase.order'

    _columns = {
        'contact_id': fields.many2one('res.partner.address.contact', 'Contact'),
    }

    def _get_vals_inv_data(self, cr, uid, order, pay_acc_id, journal_ids, inv_lines, context):
        res = super(purchase_order, self)._get_vals_inv_data(cr, uid, order, pay_acc_id, journal_ids, inv_lines, context)
        payment_term = order.partner_id.property_payment_term_payable and order.partner_id.property_payment_term_payable.id or order.partner_id.property_payment_term and order.partner_id.property_payment_term.id or False
        if payment_term:
            res['payment_term'] = payment_term
        return res

    def service_only(self, cr, uid, ids, values, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        deleted_products = []
        service = True
        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        if values and 'order_line' in values and values['order_line']:
            for line in values['order_line']:
                # create new line
                if line[0] == 0:
                    if 'product_id' in line[2] and line[2]['product_id']:
                        product = self.pool['product.product'].browse(cr, uid, line[2]['product_id'], context)
                        if not product.type == 'service':
                            if line[0] == 0:
                                return False
                elif line[0] == 2 and line[1]:
                    order_line = self.pool['purchase.order.line'].browse(cr, uid, line[1], context)
                    if order_line.product_id and not order_line.product_id.type == 'service':
                        deleted_products.append(order_line.product_id.id)
        elif not ids:
            return False
        else:
            service = False

        for order in self.browse(cr, uid, ids, context):
            if order.order_line:
                for order_line in order.order_line:
                    if order_line.product_id.type != 'service' or order_line.product_id.id in deleted_products:
                        return False
            elif not service:
                    return False
        return True

    def hook_purchase_state(self, cr, uid, ids, vals, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # function call if change state the purchase order
        return True

    @staticmethod
    def init_sequence(lines):
        for count, line in enumerate(lines, start=1):
            line[2]['sequence'] = count * 10
        return lines

    def set_sequence(self, cr, uid, lines, context=None):
        purchase_order_line_obj = self.pool['purchase.order.line']
        for count, line in enumerate(lines, start=1):
            if line[0] == 0:
                # Create
                if not 'sequence' in line[2]:
                    line[2]['sequence'] = count * 10
            elif line[0] == 1:
                # Update
                order_line = purchase_order_line_obj.read(cr, uid, line[1], ('name', 'sequence'), context)
                if not 'sequence' in line[2]:
                    line[2]['sequence'] = order_line['sequence']
            elif line[0] == 2:
                # Delete
                order_line = purchase_order_line_obj.read(cr, uid, line[1], ('name', 'sequence'), context)
                line[2] = {'sequence': order_line['sequence']}
            elif line[0] == 4:
                # Link
                order_line = purchase_order_line_obj.read(cr, uid, line[1], ('name', 'sequence'), context)
                line[0] = 1
                line[2] = {'sequence': order_line['sequence']}

        lines = sorted(lines, key=lambda line: line[2]['sequence'])

        for count, line in enumerate(lines, start=1):
            line[2]['sequence'] = count * 10

        return lines

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        company = self.pool['res.users'].browse(cr, uid, uid).company_id
        if self.service_only(cr, uid, False, vals, context) and vals.get('invoice_method', '') == 'picking':
            if company.auto_order_policy:
                vals.update({'invoice_method': 'manual'})
            else:
                raise orm.except_orm(_('Warning'), _("You can't create an order with Invoicing being based on Picking if there are only service products"))
        elif self.service_only(cr, uid, False, vals, context):
                if company.auto_order_policy:
                    vals.update({'invoice_method': 'manual'})
        else:
            if company.auto_order_policy:
                default = self.default_get(cr, uid, ['invoice_method'], context)
                vals.update({'invoice_method': default.get('invoice_method', 'manual')})
        if 'order_line' in vals:
            vals['order_line'] = self.init_sequence(vals['order_line'])

        ids = super(purchase_order, self).create(cr, uid, vals, context=context)
        if vals.get('carrier_id', False) or vals.get('payment_term', False):
            if not isinstance(ids, (list, tuple)):
                order_ids = [ids]
            order = self.browse(cr, uid, order_ids, context)[0]
            partner_vals = {}
            if not order.partner_id.property_delivery_carrier:
                partner_vals['property_delivery_carrier'] = vals.get('carrier_id')
            if not order.partner_id.property_payment_term_payable:
                partner_vals['property_payment_term_payable'] = vals.get('payment_term')
            if partner_vals:
                self.pool['res.partner'].write(cr, uid, [order.partner_id.id], partner_vals, context)
        return ids

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        for order in self.browse(cr, uid, ids, context):
            company = self.pool['res.users'].browse(cr, uid, uid).company_id
            if self.service_only(cr, uid, [order.id], vals, context) and vals.get('invoice_method', order.invoice_method) == 'picking':
                if company.auto_order_policy:
                    vals.update({'invoice_method': 'manual'})
                else:
                    raise orm.except_orm(_('Warning'), _(
                        "You can't create an order with Invoicing being based on Picking if there are only service products"))
            elif self.service_only(cr, uid, [order.id], vals, context):
                if company.auto_order_policy:
                    vals.update({'invoice_method': 'manual'})
            else:
                if company.auto_order_policy:
                    default = self.default_get(cr, uid, ['invoice_method'], context)
                    vals.update({'invoice_method': default.get('invoice_method', 'manual')})

            # adaptative function: the system learn
            if vals.get('carrier_id', False) or vals.get('payment_term', False):
                partner_vals = {}
                if not order.partner_id.property_delivery_carrier:
                    partner_vals['property_delivery_carrier'] = vals.get('carrier_id')
                if not order.partner_id.property_payment_term_payable:
                    partner_vals['property_payment_term_payable'] = vals.get('payment_term')
                if partner_vals:
                    self.pool['res.partner'].write(cr, uid, [order.partner_id.id], partner_vals, context)
            if 'order_line' in vals:
                vals['order_line'] = self.set_sequence(cr, uid, vals['order_line'], context)

        if vals.get('state', False):
            self.hook_purchase_state(cr, uid, ids, vals, context)

        return super(purchase_order, self).write(cr, uid, ids, vals, context=context)

    def onchange_fiscal_position(self, cr, uid, ids, fiscal_position, order_lines, context=None):
        '''Update taxes of order lines for each line where a product is defined

        :param list ids: not used
        :param int fiscal_position: sale order fiscal position
        :param list order_lines: command list for one2many write method
        '''
        order_line = []
        fiscal_obj = self.pool['account.fiscal.position']
        product_obj = self.pool['product.product']
        line_obj = self.pool['purchase.order.line']

        fpos = False
        if fiscal_position:
            fpos = fiscal_obj.browse(cr, uid, fiscal_position, context=context)

        for line in order_lines:
            # create    (0, 0,  { fields })
            # update    (1, ID, { fields })

            if line[0] in [0, 1]:
                prod = None
                if line[2].get('product_id'):
                    prod = product_obj.browse(cr, uid, line[2]['product_id'], context=context)
                elif line[1]:
                    prod = line_obj.browse(cr, uid, line[1], context=context).product_id
                if prod and prod.taxes_id:
                    line[2]['taxes_id'] = [[6, 0, fiscal_obj.map_tax(cr, uid, fpos, prod.supplier_taxes_id, context)]]
                order_line.append(line)

            # link      (4, ID)
            # link all  (6, 0, IDS)
            elif line[0] in [4, 6]:
                line_ids = line[0] == 4 and [line[1]] or line[2]
                for line_id in line_ids:
                    prod = line_obj.browse(cr, uid, line_id, context=context).product_id
                    if prod and prod.taxes_id:
                        order_line.append([1, line_id, {'taxes_id': [[6, 0, fiscal_obj.map_tax(cr, uid, fpos, prod.supplier_taxes_id, context)]]}])
                    else:
                        order_line.append([4, line_id])
            else:
                order_line.append(line)
        return {'value': {'order_line': order_line, 'amount_untaxed': False, 'amount_tax': False, 'amount_total': False}}

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        res = super(purchase_order, self).onchange_partner_id(cr, uid, ids, partner_id)
        supplier = self.pool['res.partner'].browse(cr, uid, partner_id)
        payment_term = supplier.property_payment_term_payable and supplier.property_payment_term_payable.id or supplier.property_payment_term and supplier.property_payment_term.id or False
        res['value'].update(
            {
                'payment_term': payment_term,
            }
        )
        return res

