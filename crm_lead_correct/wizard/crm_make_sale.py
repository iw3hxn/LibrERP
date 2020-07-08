# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.tools.translate import _


class crm_make_sale(orm.TransientModel):
    """ Make sale  order for crm """

    _inherit = "crm.make.sale"
    
    def makeOrder(self, cr, uid, ids, context=None):
        """
        This function  create Quotation on given case.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of crm make sales' ids
        @param context: A standard dictionary for contextual values
        @return: Dictionary value of created sales order.
        """
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        lead_obj = self.pool['crm.lead']
        sale_obj = self.pool['sale.order']
        partner_obj = self.pool['res.partner']
        attachment_obj = self.pool['ir.attachment']
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            partner = make.partner_id
            partner_addr = partner_obj.address_get(cr, uid, [partner.id], ['default', 'invoice', 'delivery', 'contact'])
            partner.write({'customer': True})
            pricelist_id = partner.property_product_pricelist.id
            fpos_id = partner.property_account_position and partner.property_account_position.id or False
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
            new_ids = []
            for lead in lead_obj.browse(cr, uid, data, context=context):
                if not partner and lead.partner_id:
                    partner = lead.partner_id
                    fpos_id = partner.property_account_position and partner.property_account_position.id or False
                    payment_term = partner.property_payment_term and partner.property_payment_term.id or make.shop_id.payment_default_id and make.shop_id.payment_default_id.id or False
                    partner_addr = partner_obj.address_get(cr, uid, [partner.id], ['default', 'invoice', 'delivery', 'contact'])
                    pricelist_id = partner.property_product_pricelist and partner.property_product_pricelist.id or make.shop_id.pricelist_id and make.shop_id.pricelist_id.id
                if False in partner_addr.values():
                    raise orm.except_orm(_('Data Insufficient!'), _('Customer has no addresses defined!'))

                vals = {
                    'origin': _('Opportunity: %s') % str(lead.id),
                    'section_id': lead.section_id and lead.section_id.id or False,
                    'categ_id': lead.categ_id and lead.categ_id.id or False,
                    'shop_id': make.shop_id.id,
                    'partner_id': partner.id,
                    'pricelist_id': pricelist_id,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_order_id': lead.partner_address_id and lead.partner_address_id.id or lead.partner_address_id,
                    'partner_shipping_id': lead.partner_address_id and lead.partner_address_id.id or partner_addr['delivery'],
                    'date_order': fields.date.context_today(self, cr, uid, context=context),
                    'fiscal_position': fpos_id,
                    'payment_term': payment_term,
                    'user_id': make.user_id.id,
                    # 'user_id': partner and partner.user_id and partner.user_id.id or case.user_id and case.user_id.id,
                    'note': lead.description or '',
                    'contact_id': lead.contact_id and lead.contact_id.id or False
                }
                
                new_id = sale_obj.create(cr, uid, vals, context=context)
                sale_order = sale_obj.browse(cr, uid, new_id, context=context)
                lead_obj.write(cr, uid, [lead.id], {
                    'ref': 'sale.order,%s' % new_id,
                    'sale_order_id': new_id
                }, context)
                new_ids.append(new_id)
                message = _("Opportunity  '%s' is converted to Quotation.") % (lead.name)
                self.log(cr, uid, lead.id, message)
                lead_obj.message_append(cr, uid, [lead], _("Converted to Sales Quotation(%s).") % sale_order.name, context=context)

                if make.move_attachment:
                    attachment_ids = attachment_obj.search(cr, uid, [('res_model', '=', 'crm.lead'), ('res_id', '=', lead.id)], context=context)
                    if attachment_ids:
                        attachment_obj.write(cr, uid, attachment_ids, {'res_model': 'sale.order', 'res_id': new_id}, context)
                    
            if make.close:
                lead_obj.case_close(cr, uid, data)
             
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids) <= 1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'res_id': new_ids
                }
            return value

    _columns = {
        'move_attachment': fields.boolean('Move Attachment to Quotation')
    }
    _defaults = {
        'move_attachment': True,
    }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
