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


class sale_order(orm.Model):
    _inherit = "sale.order"
    _columns = {
        'cig': fields.char('CIG', size=64, help="Codice identificativo di gara"),
        'cup': fields.char('CUP', size=64, help="Codice unico di Progetto")
    }
    
    #-----------------------------------------------------------------------------
    # EVITARE LA COPIA DI 'NUMERO cig/cup'
    #-----------------------------------------------------------------------------
    def copy(self, cr, uid, id, default={}, context=None):
        default = default or {}
        default.update({
            'cig': '',
            'cup': '',
        })
        if 'cig' not in default:
            default.update({
                'cig': False
            })
        if 'cup' not in default:
            default.update({
                'cup': False
            })

        return super(sale_order, self).copy(cr, uid, id, default, context)

    def _prepare_invoice(self, cr, uid, order, lines, context):
        invoice_vals = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context)
        invoice_vals.update({
            'cig': order.cig,
            'cup': order.cup,
        })
        return invoice_vals

    def _prepare_order_picking(self, cr, uid, order, context=None):
        picking_vals = super(sale_order, self)._prepare_order_picking(cr, uid, order, context)
        picking_vals.update({
            'cig': order.cig,
            'cup': order.cup,
        })
        return picking_vals

    # is better to use hook function, in this mode hope to speedup
    def _inv_get(self, cr, uid, order, context=None):
        return {
            'carriage_condition_id': order.carriage_condition_id.id,
            'goods_description_id': order.goods_description_id.id,
            'cig': order.cig or '',
            'cup': order.cup or ''
        }
