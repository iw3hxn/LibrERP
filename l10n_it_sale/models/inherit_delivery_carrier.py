# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Didotech SRL
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


class delivery_carrier(orm.Model):
    
    _inherit = "delivery.carrier"

    def grid_get(self, cr, uid, ids, contact_id, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        contact = self.pool['res.partner.address'].browse(cr, uid, contact_id, context=context)
        for carrier in self.browse(cr, uid, ids, context=context):
            for grid in carrier.grids_id:
                get_id = lambda x: x.id
                country_ids = map(get_id, grid.country_ids)
                state_ids = map(get_id, grid.state_ids)
                region_ids = map(get_id, grid.region_ids)
                province_ids = map(get_id, grid.province_ids)

                if country_ids and contact.country_id.id not in country_ids:
                    continue
                if state_ids and contact.state_id.id not in state_ids:
                    continue
                if province_ids and contact.province.id not in province_ids:
                    continue
                if region_ids and contact.region.id not in region_ids:
                    continue
                if grid.zip_from and (contact.zip or '') < grid.zip_from:
                    continue
                if grid.zip_to and (contact.zip or '') > grid.zip_to:
                    continue
                return grid.id

        return False

    _order = "name"

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Transport Company', required=True, domain="[('supplier', '=', True)]",
                                      help="The partner that is doing the delivery service."),
        'product_id': fields.many2one('product.product', 'Delivery Product', required=True, domain="[('type', '=', 'service')]"),
    }
