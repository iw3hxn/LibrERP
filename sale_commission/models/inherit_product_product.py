# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
#    $Id$
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

"""Modificamos las ventas para incluir el comportamiento de comisiones"""
from openerp.osv import orm, fields


class product_product(orm.Model):
    _inherit = 'product.product'
    _columns = {
        'product_agent_ids': fields.one2many('product.agent.commission', 'product_id', 'Agents'),
        'commission_exent': fields.boolean('Commission exent')
    }

    _defaults = {
        'commission_exent': lambda *a: False,
    }

    def copy(self, cr, uid, ids, default={}, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        default = default or {}
        default.update({
            'product_agent_ids': [],
            'commission_exent': False
        })

        return super(product_product, self).copy(cr, uid, ids, default, context)
