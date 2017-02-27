# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
# $Id$
#
# This program is free software: you can redistribute it and/or modify
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


class sale_agent(orm.Model):
    """Agente de ventas"""

    _name = "sale.agent"
    _description = "Sale agent"

    _columns = {
        'name': fields.char('Saleagent Name', size=125, required=True),
        'type': fields.selection((('external', 'External Commercial'), ('commercial', 'Internal Commercial')), 'Type',
                                 required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='cascade',
                                      help='Associated partner, is necessary for income invoices.'),
        'code': fields.related('partner_id', 'ref', string='Code', readonly=True, type='char',
                               help='Se obtiene del código de la empresa relacionada'),
        'employee_id': fields.many2one('hr.employee', 'Associated Employee',
                                       help='Employee associated to agent, is necessary for set an employee to settle commissions in wage.'),
        'customer': fields.one2many('res.partner.agent', 'agent_id', 'Customer', readonly=True),
        'commission': fields.many2one('commission', 'Commission by default', required=True),
        'settlement': fields.selection((('m', 'Monthly'), ('t', 'Quarterly'), ('s', 'Semiannual'), ('a', 'Annual')),
                                       'Period settlement', required=True),
        'active': fields.boolean('Active'),
        'settlement_ids': fields.one2many('settlement.agent', 'agent_id', 'Settlements executed', readonly=True),
        'section_id': fields.many2one('crm.case.section', 'Sales Team', domain=[('sale_agent_id', '=', False)], required=True),
    }

    _defaults = {
        'active': lambda *a: True,
        'type': lambda *a: 'external',
    }

    def create(self, cr, uid, values, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        res = super(sale_agent, self).create(cr, uid, values, context=context)

        if values.get('section_id', False):
            self.pool['crm.case.section'].write(cr, uid, values.get('section_id'), {'sale_agent_id': res}, context)
        return res

    def write(self, cr, uid, ids, values, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        res = super(sale_agent, self).write(cr, uid, ids, values, context=context)
        if values.get('section_id', False):
            self.pool['crm.case.section'].write(cr, uid, values.get('section_id'), {'sale_agent_id': ids[0]}, context)
        return res

    def calculate_sections(self, cr, uid, ids, base, context=None):
        """calcula los tramos por factura"""
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        agente = self.browse(cr, uid, ids, context)[0]
        return agente.commission.calculate_sections(base)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

