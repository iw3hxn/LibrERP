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


class sale_order_line_mrp_bom(orm.Model):
    _inherit = 'sale.order.line.mrp.bom'

    def _will_create_task(self, cr, uid, ids, field_name, args, context):
        result = {}
        for sale_line_bom in self.browse(cr, uid, ids, context):
            result[sale_line_bom.id] = False
            if sale_line_bom.parent_id and sale_line_bom.parent_id.type == 'service' and sale_line_bom.parent_id.supply_method == 'produce':
                result[sale_line_bom.id] = 'P'
            elif sale_line_bom.product_id.type == 'service' and not sale_line_bom.product_id.purchase_ok:
                result[sale_line_bom.id] = 'S'
        return result

    _columns = {
        'create_task': fields.function(_will_create_task, string='Will Create Task', method=True, type='char'),
    }

