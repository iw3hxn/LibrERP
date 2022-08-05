# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
# $Id$
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

"""invoice agents"""

from openerp.osv import orm, fields


class invoice_line_agent(orm.Model):
    """invoice agents"""

    _name = "invoice.line.agent"
    _inherit = "sale.order.agent"

    def _compute_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.commission_id.get_amount_order(line.invoice_id.amount_untaxed)
        return res

    _columns = {
        'invoice_line_id': fields.many2one('account.invoice.line', 'Invoice Line', required=False, ondelete='cascade'),
        'invoice_id': fields.many2one('account.invoice', required=True, ondelete='cascade', string='Invoice'),
        'invoice_date': fields.related('invoice_id.date_invoice', type='date', readonly=True),
        'settled': fields.boolean('Settled', readonly=True),
        'amount': fields.function(_compute_amount, method=True, string='Amount', type='float', store=False),
    }
    _defaults = {
        'settled': lambda *a: False,
    }

    def copy_data(self, cr, uid, ids, default=None, context=None):
        if not default:
            default = {}
        default.update({'settled': False})
        return super(invoice_line_agent, self).copy_data(cr, uid, ids, default, context=context)

    def calculate_commission(self, cr, uid, ids, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        for line_agent in self.browse(cr, uid, ids, context):
            if line_agent.commission_id.type == 'fix' and line_agent.commission_id.fix_qty:
                quantity = line_agent.invoice_line_id.price_subtotal * (line_agent.commission_id.fix_qty / 100.0)
                self.write(cr, uid, line_agent.id, {'quantity': quantity}, context)

