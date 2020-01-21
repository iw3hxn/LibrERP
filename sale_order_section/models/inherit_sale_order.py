# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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

import one2many_sorted





OPTION_SELECTION = [
    ('0', 'Base'),
    ('1', 'Alternativa 1'),
    ('2', 'Alternativa 2'),
    ('3', 'Alternativa 3'),
]


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'view_code': fields.boolean('Visualizza Codici'),
        'noshow_lineprice': fields.boolean("Nascondi Prezzo"),
        'noshow_linecode': fields.boolean("Nascondi Codice"),
        'noshow_total': fields.boolean("Nascondi Totali"),
        'order_line_base_ids': fields.one2many('sale.order.line.base', 'order_id', 'Lista Sezioni'),
        'order_line': one2many_sorted.one2many_sorted('sale.order.line', 'order_id', 'Order Lines', readonly=True,
                                                      states={'draft': [('readonly', False)]},
                                                      order='order_line_base_id.sequence ASC, sequence ASC',
                                                      # search=[('parent_id', '=', False)],
                                                      ),
        'view_total': fields.boolean(u'Visualizza Totali'),
        'view_discount': fields.boolean(u'Visualizza Sconti'),
        'view_price_unit': fields.boolean(u'Solo Lordo'),

    }

    _defaults = {
        'view_code': True,
        'view_total': True,
        'view_discount': True,
    }

    def action_check_intro(self, cr, uid, ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        order = self.browse(cr, uid, ids[0], context)
        intro_id = context.get('intro_id', False)

        if intro_id == 1:
            self.write(cr, uid, ids, {'view_total': not order.view_total}, context)
        elif intro_id == 2:
            self.write(cr, uid, ids, {'view_discount': not order.view_discount}, context)
        elif intro_id == 3:
            self.write(cr, uid, ids, {'view_price_unit': not order.view_price_unit}, context)
        elif intro_id == 4:
            self.write(cr, uid, ids, {'view_code': not order.view_code}, context)
        return True
