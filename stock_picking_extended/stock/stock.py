# -*- coding: utf-8 -*-
##############################################################################
#
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

from openerp.osv import orm, fields


class stock_journal(orm.Model):
    _inherit = "stock.journal"
    
    _columns = {
        'name': fields.char('Stock Journal', size=32, required=True, translate=True),
        }

class stock_picking(orm.Model):
    _inherit = "stock.picking"
    _columns = {
        'address_id': fields.many2one(
            'res.partner.address', 'Partner', help="Partner to be invoiced"
        ),
        'address_delivery_id': fields.many2one(
            'res.partner.address', 'Address', help='Delivery address of \
            partner'
        ),
    }

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
