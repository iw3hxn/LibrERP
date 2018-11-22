
##############################################################################
#
#    Author: Jo?l Grand-Guillaume, Guewen Baconnier
#    Copyright 2010-2012 Camptocamp SA
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
from openerp.tools.config import config

ENABLE_CACHE = config.get('product_cache', False)


class res_company(orm.Model):

    _inherit = 'res.company'

    _columns = {
        'ref_stock': fields.selection(
            [('real', 'Real Stock'),
             ('virtual', 'Virtual Stock'),
             ('immediately', 'Immediately Usable Stock')],
            'Reference Stock for BoM Stock'),
        'exclude_routing': fields.boolean('Exclude Routing on BOM Cost'),
        'exclude_consu_stock': fields.boolean('Exclude consumable from Stock')
    }

    _defaults = {
        'ref_stock': 'real',
        'exclude_routing': False
    }

    def write(self, cr, uid, ids, vals, context=None):
        res = super(res_company, self).write(cr, uid, ids, vals, context)
        if ENABLE_CACHE and 'exclude_routing' in vals:
            self.pool['product.product'].product_cost_cache.empty()
        return res

    def action_clear_cache(self, cr, uid, ids, context):
        if ENABLE_CACHE:
            self.pool['product.product'].product_cost_cache.empty()
        return True
