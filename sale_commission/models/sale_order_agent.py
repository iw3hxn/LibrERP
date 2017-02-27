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


class sale_order_agent(orm.Model):
    _name = "sale.order.agent"
    _rec_name = "agent_id"

    def name_get(self, cr, uid, ids, context=None):
        """devuelve como nombre del agente del partner el nombre del agente"""
        if context is None:
            context = {}
        res = []
        for obj in self.browse(cr, uid, ids, context):
            res.append((obj.id, obj.agent_id.name))
        return res

    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale order', required=False, ondelete='cascade', help=''),
        'agent_id': fields.many2one('sale.agent', 'Agent', required=True, ondelete='cascade', help=''),
        'commission_id': fields.many2one('commission', 'Applied commission', required=True, help=''),
    }

    def onchange_agent_id(self, cr, uid, ids, agent_id, context=None):
        """al cambiar el agente cargamos sus comisión"""
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        result = {}
        v = {}
        if agent_id:
            agent = self.pool['sale.agent'].browse(cr, uid, agent_id, context)
            v['commission_id'] = agent.commission.id

        result['value'] = v
        return result

    def onchange_commission_id(self, cr, uid, ids, agent_id=False, commission_id=False, context=None):
        """al cambiar la comisión comprobamos la selección"""
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        result = {}

        if commission_id:
            partner_commission = self.pool['commission'].browse(cr, uid, commission_id, context)
            if partner_commission.sections:
                if agent_id:
                    agent = self.pool['sale.agent'].browse(cr, uid, agent_id, context)
                    if agent.commission.id != partner_commission.id:
                        result['warning'] = {
                            'title': _('Fee installments!'),
                            'message': _(
                                'A commission has been assigned by sections that does not match that defined for the agent by default, so that these sections shall apply only on this bill.')
                        }
        return result


