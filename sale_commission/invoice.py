# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
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
        v = {}

        if agent_id:
            agent = self.pool['sale.agent'].browse(cr, uid, agent_id, context)
            v['commission_id'] = agent.commission.id

            agent_line = self.browse(cr, uid, ids, context)
            if agent_line:
                v['quantity'] = agent_line[0].invoice_line_id.price_subtotal * (agent.commission.fix_qty / 100.0)
            else:
                v['quantity'] = 0

        result['value'] = v
        return result

    def onchange_commission_id(self, cr, uid, ids, agent_id, commission_id, context=None):
        """alerta al usuario sobre la comisión elegida"""
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        result = {}
        v = {}
        if commission_id and ids:
            partner_commission = self.pool['commission'].browse(cr, uid, commission_id, context)
            agent_line = self.browse(cr, uid, ids)
            v['quantity'] = agent_line[0].invoice_line_id.price_subtotal * (partner_commission.fix_qty / 100.0)
            result['value'] = v
            if partner_commission.sections:
                if agent_id:
                    agent = self.pool['sale.agent'].browse(cr, uid, agent_id, context)

                    if agent.commission.id != partner_commission.id:
                        result['warning'] = {}
                        result['warning']['title'] = _('Fee installments!')
                        result['warning']['message'] = _(
                            'A commission has been assigned by sections that does not match that defined for the agent by default, so that these sections shall apply only on this bill.')
        return result


class account_invoice_line(orm.Model):
    """Enlazamos las comisiones a la factura"""

    _inherit = "account.invoice.line"

    _columns = {
        'commission_ids': fields.one2many('invoice.line.agent', 'invoice_line_id', 'Commissions',
                                          help="Commissions asociated to invoice line."),
    }


class account_invoice(orm.Model):
    """heredamos las facturas para añadirles el representante de venta"""

    _inherit = "account.invoice"

    _columns = {
        'section_id': fields.many2one('crm.case.section', 'Sales Team', states={'draft': [('readonly', False)]}),
        'agent_id': fields.related('section_id', 'sale_agent_id', type='many2one', relation='sale.agent',
                                   string='Agent'),
    }

    _default = {
        'section_id': lambda s, cr, uid, context: s._get_default_section_id(cr, uid, context),
    }

    def _get_default_section_id(self, cr, uid, context=None):
        """ Gives default section by checking if present in the context """
        section_id = self._resolve_section_id_from_context(cr, uid, context=context) or False
        if not section_id:
            section_id = self.pool['res.users'].browse(cr, uid, uid, context).default_section_id.id or False
        return section_id

    def onchange_partner_id(self, cr, uid, ids, type, part, date_invoice=False, payment_term=False,
                            partner_bank_id=False, company_id=False):
        """Al cambiar la empresa nos treamos el representante asociado a la empresa"""
        res = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, part, date_invoice=date_invoice,
                                                               payment_term=payment_term,
                                                               partner_bank_id=partner_bank_id, company_id=company_id)

        if part and res.get('value', False):

            section = self.pool['res.partner'].browse(cr, uid, part).section_id
            if section:
                res['value']['section_id'] = section.id

            partner = self.pool['res.partner'].browse(cr, uid, part)
            if partner.commission_ids:
                res['value']['agent_id'] = partner.commission_ids[0].agent_id.id

        return res

    def _refund_cleanup_lines(self, cr, uid, lines):
        """ugly function to map all fields of account.invoice.line when creates refund invoice"""
        res = super(account_invoice, self)._refund_cleanup_lines(cr, uid, lines)
        # import ipdb; ipdb.set_trace()
        for line in res:
            if 'commission_ids' in line[2]:
                duply_ids = []
                for cm_id in line[2].get('commission_ids', []):
                    dup_id = self.pool['invoice.line.agent'].copy(cr, uid, cm_id, {'settled': False})
                    duply_ids.append(dup_id)
                # line[2]['commission_ids'] = [(6,0, line[2].get('commission_ids', [])) ]
                line[2]['commission_ids'] = [(6, 0, duply_ids)]

        return res

    def write(self, cr, uid, ids, values, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        # TODO: set this on a function in workflow, is a wrong mode for call
        state = values.get('state', False)
        if state and state == 'open':
            for invoice in self.browse(cr, uid, ids, context):
                if invoice.agent_id:
                    vals_line = {
                        'agent_id': invoice.agent_id.id,
                        'commission_id': invoice.agent_id.commission.id
                    }

                    for invoice_line in invoice.invoice_line:
                        # qui devo sistemare tutte le righe
                        if not invoice_line.commission_ids:
                            vals_line.update({'invoice_line_id': invoice_line.id})
                            self.pool['invoice.line.agent'].create(cr, uid, vals_line, context)

        res = super(account_invoice, self).write(cr, uid, ids, values, context=context)

        return res
