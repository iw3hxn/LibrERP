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
from tools.translate import _


class invoice_line_agent(orm.Model):
    """invoice agents"""

    _name = "invoice.line.agent"

    _columns = {
        'invoice_line_id': fields.many2one('account.invoice.line', 'Invoice Line', required=False, ondelete='cascade',
                                           help=''),
        'invoice_id': fields.related('invoice_line_id', 'invoice_id', type='many2one', relation='account.invoice',
                                     string='Invoice'),
        'invoice_date': fields.related('invoice_id', type='date_invoice', readonly=True),
        'agent_id': fields.many2one('sale.agent', 'Agent', required=True, ondelete='cascade', help=''),
        'commission_id': fields.many2one('commission', 'Applied commission', required=True, help=''),
        'settled': fields.boolean('Settled', readonly=True),
        'quantity': fields.float('Settled amount')
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

    def onchange_agent_id(self, cr, uid, ids, agent_id, context=None):
        """al cambiar el agente se le carga la comisión"""
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        result = {}
        value = {}

        if agent_id:
            agent = self.pool['sale.agent'].browse(cr, uid, agent_id, context)
            value['commission_id'] = agent.commission.id

            agent_line = self.browse(cr, uid, ids, context)
            if agent_line:
                value['quantity'] = agent_line[0].invoice_line_id.price_subtotal * (agent.commission.fix_qty / 100.0)
            else:
                value['quantity'] = 0

        result['value'] = value
        return result

    def onchange_commission_id(self, cr, uid, ids, agent_id, commission_id, context=None):
        """alerta al usuario sobre la comisión elegida"""
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        result = {}
        value = {}
        if commission_id and ids:
            partner_commission = self.pool['commission'].browse(cr, uid, commission_id, context)
            agent_line = self.browse(cr, uid, ids)
            value['quantity'] = agent_line[0].invoice_line_id.price_subtotal * (partner_commission.fix_qty / 100.0)
            result['value'] = value
            if partner_commission.sections:
                if agent_id:
                    agent = self.pool['sale.agent'].browse(cr, uid, agent_id, context)

                    if agent.commission.id != partner_commission.id:
                        result['warning'] = {}
                        result['warning']['title'] = _('Fee installments!')
                        result['warning']['message'] = _(
                            'A commission has been assigned by sections that does not match that defined for the agent by default, so that these sections shall apply only on this bill.')
        return result


