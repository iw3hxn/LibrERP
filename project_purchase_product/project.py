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
from openerp.tools.translate import _


class project(orm.Model):
    _inherit = 'project.project'
    
    def _get_project_products(self, cr, uid, ids, field_name, args, context=None):
        purchase_order_line_obj = self.pool['purchase.order.line']
        result = {}
        for project in self.browse(cr, uid, ids, context):
            result[project.id] = purchase_order_line_obj.search(cr, uid, [('account_analytic_id', '=', project.analytic_account_id.id)], context=context)

        return result
    
    _columns = {
        'project_product_ids': fields.function(_get_project_products, string=_('Project products'), type='one2many', method=True, obj="purchase.order.line", multi=False)
    }
