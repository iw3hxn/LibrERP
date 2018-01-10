# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2014 Didotech srl
#    (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from tools.translate import _

from datetime import date, datetime

from openerp.osv import orm, fields
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def _credit_limit(self, cr, uid, ids, field_name, arg, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = dict.fromkeys(ids, 0.0)
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = False
            partner = picking.address_id.partner_id
            if partner:
                # We sum from all the sale orders that are aproved, the sale order lines that are not yet invoiced
                invoice_obj = self.pool['account.invoice']
                invoice_ids = invoice_obj.search(cr, uid,
                                                 [('partner_id', '=', partner.id), ('state', 'in', ['draft', 'open'])],
                                                 context=context)
                invoices_amount = 0.0
                for invoice in invoice_obj.browse(cr, uid, invoice_ids, context=context):
                    invoices_amount += invoice.amount_total
                available_credit = partner.credit_limit - invoices_amount
                res[picking.id] = available_credit
        return res

    def _get_day(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = {
                'week_nbr': False,
            }
            if not picking.minimum_planned_date:
                continue

            start_date = datetime.strptime(picking.minimum_planned_date, DEFAULT_SERVER_DATE_FORMAT)
            start_date = date(start_date.year, start_date.month, start_date.day)

            # mese in italiano start_date.strftime('%B').capitalize()
            res[picking.id] = {
                'week_nbr': start_date.isocalendar()[1]
            }

        return res

    def _get_order_type(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.type == 'internal':
                order_type = 'internal'
            else:
                order_type = 'client'
            res[picking.id] = order_type
        return res

    def _get_order_board_state(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = {
                'order_sent': False,
                'order_ready': False
            }
            if picking.state == 'done':
                res[picking.id]['order_ready'] = True
        return res

    def _get_picking_sale(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        stock_picking_model = self.pool['stock.picking']
        picking_ids = stock_picking_model.search(cr, uid, [('sale_id', 'in', ids)], context=context)
        for picking in stock_picking_model.browse(cr, uid, picking_ids, context):
            result[picking.id] = True
        return result.keys()

    _columns = {
        'goods_ready': fields.related('move_lines', 'goods_ready', type='boolean', string='Goods Ready'),
        'carriage_condition_id': fields.many2one(
            'stock.picking.carriage_condition', 'Carriage condition'),
        'goods_description_id': fields.many2one(
            'stock.picking.goods_description', 'Description of goods'),
        'transportation_condition_id': fields.many2one(
            'stock.picking.transportation_condition', 'Transportation condition'),
        # address_id is overridden because it's used 2binvoiced
        # n.b.: partner_id is only a related, so not useful for the workflow
        'address_id': fields.many2one(
            'res.partner.address', 'Partner', help="Partner to be invoiced"
        ),
        'address_delivery_id': fields.many2one(
            'res.partner.address', 'Address', help='Delivery address of \
            partner'
        ),
        'invoice_state': fields.selection([
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable")], "Invoice Control",
            select=True, required=True, readonly=False),
        'client_order_ref': fields.related(
            'sale_id', 'client_order_ref', type='char',
            string='Customer Reference'),
        'credit_limit': fields.function(_credit_limit, string="Remaining Credit Limit", type='float', readonly=True,
                                        method=True),
        'visible_credit_limit': fields.related('company_id', 'check_credit_limit', type='boolean',
                                               string=_('Fido Residuo Visibile'), store=False, readonly=True),
        # 'weight': fields.float('Gross weight', digits_compute=dp.get_precision('Stock Weight'), help="The gross weight in Kg."),
        # 'weight_net': fields.float('Net weight', digits_compute=dp.get_precision('Stock Weight'), help="The net weight in Kg."),
        'customer_id': fields.related('sale_id', 'partner_id', type='many2one', relation='res.partner',
                                      string='Customer', store=False, readonly=True),
        'order_type': fields.function(_get_order_type, string="Order Type", type="selection", selection=[
            ('client', 'Client'),
            ('internal', 'Internal'),
        ], readonly=True),
        'order_sent': fields.function(_get_order_board_state, type='boolean', multi='order_state', string='Order Sent'),
        'order_ready': fields.function(_get_order_board_state, type='boolean', multi='order_state', string='Order Ready'),
        'creation_date': fields.related('sale_id', 'create_date', type='date', string='Inserted on', store=False,
                                        readonly=True),
        'street': fields.related('address_id', 'street', type='char', string='Street', store=False),
        'city': fields.related('address_id', 'city', type='char', string='City', store=False),
        'province': fields.related('address_id', 'province', type='many2one', relation='res.province',
                                   string='Province', store=False, readonly=True),
        'region': fields.related('address_id', 'region', type='many2one', relation='res.region', string='Region',
                                 store=False, readonly=True),
        'agent': fields.related('customer_id', 'section_id', type='many2one', relation='crm.case.section',
                                string='Agent', store=False, readonly=True),
        'board_date': fields.date('Order Board Delivery date'),
        'amount_total': fields.related('sale_id', 'amount_untaxed', type='float', string='Total Amount (VAT Excluded)',
                                       readonly=True),
        'week_nbr': fields.function(_get_day, method=True, multi='day_of_week', type="integer", string="Week Number",
                                    store={
                                        'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['max_date'], 5000),
                                        'sale.order': (_get_picking_sale, ['minimum_planned_date'], 5000),
                                        }),

        'minimum_planned_date': fields.related('sale_id', 'minimum_planned_date', type='date', string='Expected Date'),
        'internal_note': fields.char('Internal Note')
    }

    def check_limit(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.type == 'out':
                if picking.credit_limit < 0 and picking.company_id and picking.company_id.check_credit_limit:
                    title = _(u'Credit Over Limit')
                    msg = _(u'Is not possible to confirm because customer exceed the credit limit.')
                    raise orm.except_orm(_(title), _(msg))
                    return False
                if picking.company_id and picking.company_id.check_overdue and self.pool[
                    'sale.order'].partner_overdue_check(cr, uid, picking.company_id, picking.address_id.partner_id,
                                                        context):
                    title = _(u'Overdue Limit')
                    msg = _(u'Is not possible to confirm because customer have a overdue payment.')
                    raise orm.except_orm(_(title), _(msg))
                    return False
        return True

    def action_process(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if self.check_limit(cr, uid, ids, context):
            return super(stock_picking, self).action_process(cr, uid, ids, context=context)
        else:
            return False

    def print_picking(self, cr, uid, ids, context):
        return self.pool['account.invoice'].print_report(cr, uid, ids, 'delivery.report_shipping', context)

    def onchange_stock_journal(self, cr, uid, ids, stock_journal_id=None, state=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if state != 'draft':
            return {'value': {}}

        stock_journal_obj = self.pool['stock.journal']
        default_invoice_state = False
        if stock_journal_id:
            default_invoice_state = stock_journal_obj.browse(
                cr, uid, stock_journal_id, context).default_invoice_state

        return {'value': {'invoice_state': default_invoice_state or 'none'}}

    def onchange_partner_in(self, cr, uid, ids, address_id=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        partner_address_obj = self.pool['res.partner.address']
        delivery_ids = []
        partner_id = None
        if address_id:
            partner_id = partner_address_obj.browse(
                cr, uid, address_id, context).partner_id
        if partner_id:
            delivery_ids = partner_address_obj.search(
                cr, uid, [('partner_id', '=', partner_id.id), (
                    'default_delivery_partner_address', '=', True)],
                context=context
            )

            if not delivery_ids:
                delivery_ids = partner_address_obj.search(
                    cr, uid, [('partner_id', '=', partner_id.id), (
                        'type', '=', 'delivery')],
                    context=context
                )
                if not delivery_ids:
                    delivery_ids = partner_address_obj.search(
                        cr, uid, [('partner_id', '=', partner_id.id)],
                        context=context
                    )

        if delivery_ids:
            return {'value': {'address_delivery_id': delivery_ids[0]}}
        else:
            return {'value': {}}

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        context = context or self.pool['res.users'].context_get(cr, uid)
        new_args = []
        if context.get('order', False):
            order = context['order']

        for arg in args:
            # if arg and len(arg)==3 and arg[0] in field_to_sql.keys() and arg[1]=='ilike':
            if arg and len(arg) == 3 and arg[1] == 'ilike':
                values = arg[2].split(',')
                if values > 1:
                    new_args += ['|' for x in range(len(values) - 1)] + [(arg[0], arg[1], value.strip()) for value in
                                                                         values]
            else:
                new_args.append(arg)

        return super(stock_picking, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order,
                                                 context=context, count=count)

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if ('name' not in vals) or (vals.get('name') == '/'):
            if 'type' in vals.keys() and vals['type'] == 'out':
                vals['name'] = self.pool['ir.sequence'].next_by_code(cr, uid, 'stock.picking.out')
            elif 'type' in vals.keys() and vals['type'] == 'internal':
                vals['name'] = self.pool['ir.sequence'].next_by_code(cr, uid, 'stock.picking.internal')
            else:
                vals['name'] = self.pool['ir.sequence'].next_by_code(cr, uid, 'stock.picking.in')
        ids = super(stock_picking, self).create(cr, uid, vals, context)

        if vals.get('carriage_condition_id', False) or vals.get('goods_description_id', False):
            picking = self.browse(cr, uid, ids, context)
            partner_vals = {}
            if not picking.partner_id.carriage_condition_id:
                partner_vals['carriage_condition_id'] = vals.get('carriage_condition_id')
            if not picking.partner_id.goods_description_id:
                partner_vals['goods_description_id'] = vals.get('goods_description_id')
            if not picking.partner_id.property_delivery_carrier:
                partner_vals['property_delivery_carrier'] = vals.get('carrier_id')
            if partner_vals:
                self.pool['res.partner'].write(cr, uid, [picking.partner_id.id], partner_vals, context)
        return ids

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=None):
        res = super(stock_picking, self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id,
                                                               invoice_vals, context=context)
        """ Update dict with correct shipped qty
        """
        res['quantity'] = move_line.product_qty or move_line.product_uos_qty
        return res

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
                              group=False, type='out_invoice', context=None):
        res = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id,
                                                               group, type, context)

        for picking in self.browse(cr, uid, ids, context=context):
            self.pool['account.invoice'].write(cr, uid, res[picking.id], {
                'carriage_condition_id': picking.carriage_condition_id.id,
                'goods_description_id': picking.goods_description_id.id,
                'transportation_condition_id': picking.transportation_condition_id.id,
            }, context)
            if picking.sale_id:
                for order_line in picking.sale_id.order_line:
                    if not order_line.invoiced:
                        break
                else:
                    sale_order = self.pool['sale.order'].browse(cr, uid, picking.sale_id.id, context)
                    if sale_order.state == 'manual':
                        sale_order.write({'state': 'progress'})

        return res

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        context = self.pool['res.users'].context_get(cr, uid)
        company_id = self.pool['res.users'].get_current_company(cr, uid)[0][0]
        company = self.pool['res.company'].browse(cr, uid, company_id, context)
        if company.note_on_invoice_line:
            self.pool['account.invoice.line'].write(cr, uid, invoice_line_id, {'note': move_line.note}, context)
        return super(stock_picking, self)._invoice_line_hook(cr, uid, move_line, invoice_line_id)
