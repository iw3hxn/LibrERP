# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Didotech SRL (info at didotech.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import orm, fields

COLOR_SELECTION = [('aqua', (u"Aqua")),
                   ('black', (u"Black")),
                   ('blue', (u"Blue")),
                   ('brown', (u"Brown")),
                   ('cadetblue', (u"Cadet Blue")),
                   ('darkblue', (u"Dark Blue")),
                   ('fuchsia', (u"Fuchsia")),
                   ('forestgreen', (u"Forest Green")),
                   ('green', (u"Green")),
                   ('grey', (u"Grey")),
                   ('red', (u"Red")),
                   ('orange', (u"Orange"))
                   ]


class CrmCaseCateg(orm.Model):
    _inherit = 'crm.case.categ'

    def _get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        for categ in self.read(cr, uid, ids, ['color'], context):
            if categ['color']:
                value[categ['id']] = categ['color']
            else:
                value[categ['id']] = 'black'

        return value

    def _compute_crm_order_number(self, cr, uid, ids, field_name, arg, context):
        value = {}
        crm_lead_model = self.pool['crm.lead']
        for categ_id in ids:
            value[categ_id] = crm_lead_model.search(cr, uid, [('categ_id', '=', categ_id)], context=context, count=True)

        return value

    def _compute_sale_order_number(self, cr, uid, ids, field_name, arg, context):
        value = {}
        sale_order_model = self.pool['sale.order']
        for categ_id in ids:
            value[categ_id] = sale_order_model.search(cr, uid, [('categ_id', '=', categ_id)], context=context, count=True)

        return value

    _columns = {
        'active': fields.boolean("Active"),
        'sequence': fields.integer('Sequence'),
        'name': fields.char('Name', size=64, required=True, translate=False),
        'color': fields.selection(COLOR_SELECTION, 'Color'),
        'row_color': fields.function(_get_color, 'Row color', type='char', readonly=True, method=True,),
        'crm_order_number': fields.function(_compute_crm_order_number, string='CRM #', type='integer',
                                             readonly=True),
        'sale_order_number': fields.function(_compute_sale_order_number, string='Sale Order #', type='integer', readonly=True)
    }

    _defaults = {
        'sequence': 10,
        "active": True
    }

    _order = "sequence, name"
