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


class product_agent_commission(orm.Model):
    _name = "product.agent.commission"
    _rec_name = "commission_id"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=False, ondelete='cascade', help=''),
        'commission_id': fields.many2one('commission', 'Applied commission', required=True, help=''),
        'agent_ids': fields.many2many('sale.agent', 'product_agent_sale_agent_rel', 'product_commission_id', 'agent_id',
                                      'Agents'),
    }


