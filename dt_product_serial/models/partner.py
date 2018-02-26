# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
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


class res_partner(orm.Model):
    _inherit = 'res.partner'
    
    def _get_pallets(self, cr, uid, ids, field_name, args, context=None):
        result = {}
        
        pallet_type_ids = self.pool['product.ul'].search(cr, uid, [('type', '=', 'pallet')], context=context)
        
        for partner_id in ids:
            result[partner_id] = pallet_type_ids or []
        
        return result
        
    _columns = {
        'pallet_ids': fields.function(_get_pallets, relation='product.ul', string='Pallets', type="one2many", method=True, multi=False),
    }
