# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
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

from openerp.osv import orm, fields


class stock_picking_carriage_condition(orm.Model):
    """
    Carriage condition
    """
    _name = "stock.picking.carriage_condition"
    _description = "Carriage Condition"
    _columns = {
        'name': fields.char('Carriage Condition', size=64, required=True, readonly=False, translable=True),
        'note': fields.text('Note'),
    }


class stock_picking_goods_description(orm.Model):
    """
    Description of Goods
    """
    _name = 'stock.picking.goods_description'
    _description = "Description of Goods"

    _columns = {
        'name': fields.char('Description of Goods', size=64, required=True, readonly=False, translable=True),
        'note': fields.text('Note'),
    }


class stock_picking_transportation_condition(orm.Model):
    """
    transportation condition
    """
    _name = "stock.picking.transportation_condition"
    _description = "Transportation Condition"
    _columns = {
        'name': fields.char('transportation Condition', size=64, required=True, readonly=False, translable=True),
        'note': fields.text('Note'),
    }


class stock_picking(orm.Model):
    _inherit = "stock.picking"
    _columns = {
        'carriage_condition_id': fields.many2one('stock.picking.carriage_condition', 'Carriage condition'),
        'goods_description_id': fields.many2one('stock.picking.goods_description', 'Description of goods'),
        'transportation_condition_id': fields.many2one('stock.picking.transportation_condition', 'transportation condition'),
        'address_id': fields.many2one(
            'res.partner.address', 'Partner', help="Partner to be invoiced"
        ),
        'address_delivery_id': fields.many2one(
            'res.partner.address', 'Address', help='Delivery address of \
            partner'
        ),
    }
    
    def onchange_stock_journal(self, cr, uid, context=None, stock_journal_id=None, state=None):
        if context is None:
            context = {}
        
        if state != 'draft':
            return {'value': {}}
        
        stock_journal_obj = self.pool['stock.journal']
        if stock_journal_id:
            default_invoice_state = stock_journal_obj.browse(
                    cr, uid, stock_journal_id, context).default_invoice_state
        
        if default_invoice_state: 
            return {'value': {'invoice_state': default_invoice_state}}
        else:
            return {'value': {'invoice_state': 'none'}}
        return {'value': {}}
    
    def onchange_partner_in(self, cr, uid, context=None, partner_address_id=None):
        if context is None:
            context = {}
        result = super(stock_picking, self).onchange_partner_in(
            cr, uid, context, partner_address_id
        )
        partner_address_obj = self.pool['res.partner.address']
        delivery_ids = []
        
        partner_id = None
        if partner_address_id:
            partner_id = partner_address_obj.browse(cr, uid, partner_address_id, context).partner_id
        if partner_id:
            delivery_ids = partner_address_obj.search(
                cr, uid, [('partner_id', '=', partner_id.id), (
                    'default_delivery_partner_address', '=', True)],
                context
            )
            
            if not delivery_ids:
                delivery_ids = partner_address_obj.search(
                    cr, uid, [('partner_id', '=', partner_id.id), (
                        'type', '=', 'delivery')],
                    context
                )
                if not delivery_ids:
                    delivery_ids = partner_address_obj.search(
                        cr, uid, [('partner_id', '=', partner_id.id)],
                        context
                    )

        if delivery_ids:
            result['value']['address_delivery_id'] = delivery_ids[0]
        
        return result
    
    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        new_args = []
        
        for arg in args:
            #if arg and len(arg)==3 and arg[0] in field_to_sql.keys() and arg[1]=='ilike':
            if arg and len(arg) == 3 and arg[1] == 'ilike':
                values = arg[2].split(',')
                if values > 1:
                    new_args += ['|' for x in range(len(values) - 1)] + [(arg[0], arg[1], value.strip()) for value in values]
            else:
                new_args.append(arg)
        
        return super(stock_picking, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name') == '/'):
            if 'type' in vals.keys() and vals['type'] == 'out':
                vals['name'] = self.pool['ir.sequence'].next_by_code(cr, user, 'stock.picking.out')
            elif 'type' in vals.keys() and vals['type'] == 'internal':
                vals['name'] = self.pool['ir.sequence'].next_by_code(cr, user, 'stock.picking.internal')
            else:
                vals['name'] = self.pool['ir.sequence'].next_by_code(cr, user, 'stock.picking.in')

        return super(stock_picking, self).create(cr, user, vals, context)

    def action_invoice_create(self, cursor, user, ids, journal_id=False,
                              group=False, type='out_invoice', context=None):
        res = super(stock_picking, self).action_invoice_create(cursor, user, ids, journal_id,
                                                               group, type, context)
        for picking in self.browse(cursor, user, ids, context=context):
            self.pool['account.invoice'].write(cursor, user, res[picking.id], {
                'carriage_condition_id': picking.carriage_condition_id.id,
                'goods_description_id': picking.goods_description_id.id,
                'transportation_condition_id': picking.transportation_condition_id.id,
            })
        return res