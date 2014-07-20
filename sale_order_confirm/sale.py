#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyraght (c) 2013-2014 Didotech srl (<http://www.didotech.com>)
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
import decimal_precision as dp


class sale_order(orm.Model):
    _inherit = "sale.order"
    
    def onchange_invoice_type_id(self, cr, uid, ids, invoice_type_id, context=None):
        res = {}
        if invoice_type_id:
            invoice_type_obj = self.pool['sale_journal.invoice.type']
            invoice_type = invoice_type_obj.browse(cr, uid, invoice_type_id)
            if invoice_type.invoicing_method == 'grouped':
                res['order_policy'] = 'picking'
        return {'value': res}
    
    def _credit_limit(self, cr, uid, ids, field_name, arg, context):
        res = dict.fromkeys(ids, 0.0)
        for order_id in ids:
            processed_order = self.browse(cr, uid, order_id, context=context)
            if processed_order.order_policy == 'prepaid':
                continue
            partner = processed_order.partner_id
            credit = partner.credit
            # We sum from all the sale orders that are aproved, the sale order lines that are not yet invoiced
            order_obj = self.pool['sale.order']
            filters = [('partner_id', '=', partner.id), ('state', '<>', 'draft'), ('state', '<>', 'cancel')]
            approved_invoices_ids = order_obj.search(cr, uid, filters, context=context)
            approved_invoices_amount = 0.0
            for order in order_obj.browse(cr, uid, approved_invoices_ids, context=context):
                for order_line in order.order_line:
                    if not order_line.invoiced:
                        approved_invoices_amount += order_line.price_subtotal
            
            # We sum from all the invoices that are in draft the total amount
            invoice_obj = self.pool['account.invoice']
            filters = [('partner_id', '=', partner.id), ('state', '=', 'draft')]
            draft_invoices_ids = invoice_obj.search(cr, uid, filters, context=context)
            draft_invoices_amount = 0.0
            for invoice in invoice_obj.browse(cr, uid, draft_invoices_ids, context=context):
                draft_invoices_amount += invoice.amount_total
            available_credit = partner.credit_limit - credit - approved_invoices_amount - draft_invoices_amount
            res[order_id] = available_credit - processed_order.amount_total
        return res
    
    def check_limit(self, cr, uid, ids, context=None):
        for order_id in ids:
            processed_order = self.browse(cr, uid, order_id, context=context)
            
            if processed_order.order_policy == 'prepaid':
                continue
            
            partner = processed_order.partner_id
            credit = partner.credit
            
            # We sum from all the sale orders that are aproved, the sale order lines that are not yet invoiced
            order_obj = self.pool['sale.order']
            filters = [('partner_id', '=', partner.id), ('state', '<>', 'draft'), ('state', '<>', 'cancel')]
            approved_invoices_ids = order_obj.search(cr, uid, filters, context=context)
            approved_invoices_amount = 0.0
            for order in order_obj.browse(cr, uid, approved_invoices_ids, context=context):
                for order_line in order.order_line:
                    if not order_line.invoiced:
                        approved_invoices_amount += order_line.price_subtotal
            
            # We sum from all the invoices that are in draft the total amount
            invoice_obj = self.pool['account.invoice']
            filters = [('partner_id', '=', partner.id), ('state', '=', 'draft')]
            draft_invoices_ids = invoice_obj.search(cr, uid, filters, context=context)
            draft_invoices_amount = 0.0
            for invoice in invoice_obj.browse(cr, uid, draft_invoices_ids, context=context):
                draft_invoices_amount += invoice.amount_total
            
            available_credit = partner.credit_limit - credit - approved_invoices_amount - draft_invoices_amount
            # check if is anable credit check in the company
            if (processed_order.amount_total > available_credit) and processed_order.company_id and processed_order.company_id.check_credit_limit:
                title = 'Fido Superato!'
                msg = 'Non è possibile confermare in quanto il cliente non ha fido sufficiente.'
                title = 'Fido Superato'
                msg = u'Non è possibile confermare in quanto il cliente non ha fido sufficiente. \
                         È possibile cambiare la politica di fatturazione a "pagamento prima della consegna" \
                         nella scheda "Altre informazioni"'

                raise orm.except_orm(_(title), _(msg))
                return False
        return True
        
    _columns = {
        'credit_limit': fields.function(_credit_limit, string="Fido Residuo", type='float', readonly=True, method=True),
        'visible_credit_limit': fields.related('company_id', 'check_credit_limit', type='boolean', string=_('Fido Residuo Visibile'), store=False, readonly=True),
        'validity': fields.date('Validity'),
        'state': fields.selection([
            ('draft', _('Quotation')),
            ('wait_technical_validation', _('Technical Validation')),
            ('wait_manager_validation', _('Manager Validation')),
            ('send_to_customer', _('Send To Customer')),
            ('wait_customer_validation', _('Customer Validation')),
            ('waiting_date', _('Waiting Schedule')),
            ('manual', _('To Invoice')),
            ('progress', _('In Progress')),
            ('shipping_except', _('Shipping Exception')),
            ('invoice_except', _('Invoice Exception')),
            ('done', _('Done')),
            ('cancel', _('Cancelled'))
        ], 'Order State', readonly=True, help="Gives the state of the quotation or sales order. \nThe exception state is automatically set when a cancel operation occurs in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception). \nThe 'Waiting Schedule' state is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True),
        'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={
            'draft': [('readonly', False)],
            'wait_technical_validation': [('readonly', False)],
            'wait_manager_validation': [('readonly', False)]}
        ),
        'project_id': fields.many2one('account.analytic.account', 'Contract/Analytic Account', readonly=True, states={
            'draft': [('readonly', False)],
            'wait_technical_validation': [('readonly', False)],
            'wait_manager_validation': [('readonly', False)],
            'send_to_customer': [('readonly', False)],
            'wait_customer_validation': [('readonly', False)],
        }, help="The analytic account related to a sales order."),
        'required_tech_validation': fields.related('company_id', 'need_tech_validation', type='boolean', string=_('Required Technical Validation'), store=False, readonly=True),
        'need_tech_validation': fields.boolean("Technical Validation", readonly=True),
        'tech_validation': fields.boolean("Tech Validated ?", readonly=True),
        'required_manager_validation': fields.related('company_id', 'need_manager_validation', type='boolean', string=_('Required Manager Validation'), store=False, readonly=True),
        'need_manager_validation': fields.boolean("Manager Validation", readonly=True),
        'manager_validation': fields.boolean("Manager Validated ?", readonly=True),
        'email_sent_validation': fields.boolean("Email Sent to Customer ?", readonly=True),
        'customer_validation': fields.boolean("Customer Validated ?", readonly=True),
        'revision_note': fields.char('Reason', size=256, select=True),
        'last_revision_note': fields.related('sale_version_id', 'revision_note', type='char', string="Last Revision Note", store=True),
    }
    
    _defaults = {
        'need_tech_validation': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.need_tech_validation,
        'need_manager_validation': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.need_manager_validation,
        'required_tech_validation': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.need_tech_validation,
        'required_manager_validation': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.need_manager_validation,
    }
    
    def action_validate(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids):
            if o.need_tech_validation and not o.tech_validation:
                self.write(cr, uid, [o.id], {'state': 'wait_technical_validation'})
            elif o.company_id.enable_margin_validation and o.amount_untaxed and (o.margin / o.amount_untaxed) < o.company_id.minimum_margin and not o.manager_validation:
                self.write(cr, uid, [o.id], {'state': 'wait_manager_validation'})
            elif o.need_manager_validation and not o.manager_validation:
                self.write(cr, uid, [o.id], {'state': 'wait_manager_validation'})
            elif not o.email_sent_validation:
                self.write(cr, uid, [o.id], {'state': 'send_to_customer'})
            elif not o.customer_validation:
                self.write(cr, uid, [o.id], {'state': 'wait_customer_validation'})
            else:
                self.write(cr, uid, [o.id], {'state': 'send_to_customer'})
        return True
    
    def check_validate(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids):
            res = True
            
            if o.need_tech_validation and not o.tech_validation:
                res = False
            if o.need_manager_validation and not o.manager_validation:
                res = False
            return res and o.email_sent_validation and o.customer_validation
        return True
    
    def check_direct_confirm(self, cr, uid, ids, context=None):
        if self.check_limit(cr, uid, ids, context):
            for order in self.browse(cr, uid, ids):
                values = {
                    'state': 'wait_customer_validation',
                    'customer_validation': True
                }
                if order.need_tech_validation:
                    values['tech_validation'] = True
                
                if (order.company_id.enable_margin_validation and order.amount_untaxed and (order.margin / order.amount_untaxed) < order.company_id.minimum_margin) or order.need_manager_validation:
                    values['manager_validation'] = True
                
                self.write(cr, uid, [order.id], values)
            
            return self.action_validate(cr, uid, ids, context)
        else:
            return False
       
    def copy(self, cr, uid, order_id, defaults, context=None):
        defaults['customer_validation'] = False
        defaults['email_sent_validation'] = False
        
        return super(sale_order, self).copy(cr, uid, order_id, defaults, context)


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"
    
    def _delivered_qty(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            qty = 0
            
            for move in line.move_ids:
                if move.state == 'done':
                    qty += move.product_qty
                    
            res[line.id] = qty
        return res
    
    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """

        if context is None:
            context = {}
        res = {}
        
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = {'qty_available': line.product_id and line.product_id.qty_available or 0.0,
                            'virtual_available': line.product_id and line.product_id.virtual_available or 0.0}
        return res

    #overwrite of funcion insede sale_margin
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
                                                             uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
                                                             lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        if not pricelist:
            return res
        frm_cur = self.pool['res.users'].browse(cr, uid, uid, context).company_id.currency_id.id
        to_cur = self.pool['product.pricelist'].browse(cr, uid, [pricelist], context)[0].currency_id.id
        if product:
            product_id = self.pool['product.product'].browse(cr, uid, product, context)
            purchase_price = product_id.cost_price
            product_type = product_id.type
            
            price = self.pool['res.currency'].compute(cr, uid, frm_cur, to_cur, purchase_price, round=False)
            res['value'].update({'purchase_price': price,
                                 'product_type': product_type})
            
        return res
   
    _columns = {
        'order_id': fields.many2one('sale.order', 'Order Reference', ondelete='cascade', select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'readonly_price_unit': fields.related('order_id', 'company_id', 'need_tech_validation', type='boolean', string=_('Readonly Price Unit'), store=False, readonly=True),
        'delivered_qty': fields.function(_delivered_qty, digits_compute=dp.get_precision('Product UoM'), string='Delivered Qty'),
        'qty_available': fields.function(_product_available, multi='qty_available',
                                         type='float', digits_compute=dp.get_precision('Product UoM'),
                                         string='Quantity On Hand'),
        'virtual_available': fields.function(_product_available, multi='qty_available',
                                             type='float', digits_compute=dp.get_precision('Product UoM'),
                                             string='Quantity Available'),
        'product_type': fields.char('Product type', size=64),
        
        #'pricelist_id': fields.related('order_id', 'pricelist_id', type='many2one', relation='product.pricelist', string='Pricelist'),
        #'partner_id': fields.related('order_id', 'partner_id', type='many2one', relation='res.partner', string='Customer'),
        #'date_order':fields.related('order_id', 'date_order', type="date", string="Date"),
        #'fiscal_position': fields.related('order_id', 'fiscal_position', type='many2one', relation='account.fiscal.position', string='Fiscal Position'),
        #'shop_id': fields.related('order_id', 'shop_id', type='many2one', relation='sale.shop', string='Shop'),
    }
    
    _defaults = {
        'readonly_price_unit': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid, context).company_id.readonly_price_unit,
        #'pricelist_id': lambda self, cr, uid, c: c.get('pricelist_id', False),
        #'partner_id': lambda self, cr, uid, c: c.get('partner_id', False),
        #'date_order': lambda self, cr, uid, c: c.get('date_order', False),
        #'fiscal_position': lambda self, cr, uid, c: c.get('fiscal_position', False),
        #'shop_id': lambda self, cr, uid, c: c.get('shop_id', False),
        'order_id': lambda self, cr, uid, context: context.get('default_sale_order', False) or False
    }
