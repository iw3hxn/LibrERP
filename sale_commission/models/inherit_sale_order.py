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
from tools.translate import _


class sale_order(orm.Model):
    """Modificamos las ventas para incluir el comportamiento de comisiones"""

    _inherit = "sale.order"

    _columns = {
        'sale_agent_ids': fields.one2many('sale.order.agent', 'sale_id', 'Agents', readonly=False),
        'section_id': fields.many2one('crm.case.section', 'Sales Team', required=True),
    }

    def onchange_partner_id(self, cr, uid, ids, part):
        """heredamos el evento de cambio del campo partner_id para actualizar el campo agent_id"""
        context = self.pool['res.users'].context_get(cr, uid)

        sale_agent_ids = []
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part)
        sale_order_agent = self.pool['sale.order.agent']

        ids and sale_order_agent.unlink(cr, uid, sale_order_agent.search(cr, uid, [('sale_id', 'in', ids)]), context)

        if res.get('value', False) and part:
            partner = self.pool['res.partner'].browse(cr, uid, part, context)
            if partner.section_id and partner.section_id.sale_agent_id:
                vals = {
                        'agent_id': partner.section_id.sale_agent_id.id,
                        'commission_id': partner.section_id.sale_agent_id.commission.id,
                }
                sale_agent_id = sale_order_agent.create(cr, uid, vals, context)
                sale_agent_ids.append(int(sale_agent_id))
            else:
                for partner_agent in partner.commission_ids:
                    vals = {
                        'agent_id': partner_agent.agent_id.id,
                        'commission_id': partner_agent.commission_id.id,
                    }
                    if ids:
                        for id in ids:
                            vals['sale_id'] = id
                    sale_agent_id = sale_order_agent.create(cr, uid, vals, context)
                    sale_agent_ids.append(int(sale_agent_id))

            res['value']['sale_agent_ids'] = sale_agent_ids
        return res

    def action_ship_create(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        """extend this method to add agent_id to picking"""
        res = super(sale_order, self).action_ship_create(cr, uid, ids, context)

        for order in self.browse(cr, uid, ids, context):
            pickings = [x.id for x in order.picking_ids]
            agents = [x.agent_id.id for x in order.sale_agent_ids]
            if pickings and agents:
                self.pool['stock.picking'].write(cr, uid, pickings, {'agent_ids': [[6, 0, agents]]}, context)
        return res

    def create(self, cr, uid, values, context=None):
        """
        Para que el cliente gtk no borre el agente al darle a guardar
        """
        res = super(sale_order, self).create(cr, uid, values, context)
        if 'sale_agent_ids' in values:
            for sale_order_agent in values['sale_agent_ids']:
                if sale_order_agent[1]:
                    self.pool['sale.order.agent'].write(cr, uid, [sale_order_agent[1]], {'sale_id': res}, context)
        return res


