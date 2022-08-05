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

import decimal_precision as dp
"""invoice agents"""

from openerp.osv import orm, fields
from tools.translate import _


class account_invoice(orm.Model):
    """heredamos las facturas para añadirles el representante de venta"""

    _inherit = "account.invoice"

    def _compute_sale_agent_commission(self, cr, uid, ids, name, arg, context=None):

        context = context or self.pool['res.users'].context_get(cr, uid)
        agent_id = int(context.get('agent_id', 0))
        invoice_line_agent_model = self.pool["invoice.line.agent"]
        res = {}
        for invoice_id in ids:
            rule = invoice_line_agent_model.search_browse(cr, uid, [('invoice_id', '=', invoice_id), ('agent_id', '=', agent_id) ], context=context, limit=1)
            res[invoice_id] = rule and rule.amount or 0.0
        return res

    def _compute_sale_agent_list(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            agents = []
            for agent in invoice.sale_agent_ids:
                agents.append(agent.agent_id.name)

            res[invoice.id] = ', '.join(agents)
        return res

    _columns = {
        'section_id': fields.many2one('crm.case.section', 'Sales Team', domain=[('sale_agent_id', '!=', False)],
                                      states={'draft': [('readonly', False)]}),

        'agent_id': fields.related('sale_agent_ids', 'agent_id', type='many2one', relation='sale.agent',
                                   string='Agent'),
        'sale_order_ids': fields.many2many(
            'sale.order', 'sale_order_invoice_rel', 'invoice_id', 'order_id', 'Sale orders'
        ),
        'sale_agent_ids': fields.one2many('invoice.line.agent', 'invoice_id', 'Agents', readonly=False),
        'sale_agent_list': fields.function(_compute_sale_agent_list, type='text', string='Agents'),
        'sale_agent_commission': fields.function(_compute_sale_agent_commission, type='float', string='Sale Commission',
                                                 digits_compute=dp.get_precision('Sale Price')),
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
        context = self.pool['res.users'].context_get(cr, uid)
        sale_order_agent = self.pool['invoice.line.agent']
        ids and sale_order_agent.unlink(cr, uid, sale_order_agent.search(cr, uid, [('invoice_id', 'in', ids)]), context)
        sale_agent_ids = []
        if part and res.get('value', False):
            partner = self.pool['res.partner'].browse(cr, uid, part, context)
            section = partner.section_id
            if section:
                res['value']['section_id'] = section.id
            if partner.section_id and partner.section_id.sale_agent_id:
                vals = {
                    'commission_id': partner.section_id.sale_agent_id.commission.id,
                }
                sale_agent_id = sale_order_agent.create(cr, uid, vals, context)
                sale_agent_ids.append(int(sale_agent_id))
            else:
                for partner_agent in partner.commission_ids:
                    vals = {
                        'agent_id': partner_agent.agent_id.id,
                        'commission_id': partner_agent.commission_id.id,
                        'invoice_id': ids and ids[0] or False
                    }
                    sale_agent_id = sale_order_agent.create(cr, uid, vals, context)
                    sale_agent_ids.append(int(sale_agent_id))

            if partner.commission_ids:
                res['value']['agent_id'] = partner.commission_ids[0].agent_id.id

            res['value']['sale_agent_ids'] = sale_agent_ids

        return res

    def _refund_cleanup_lines(self, cr, uid, lines):
        """ugly function to map all fields of account.invoice.line when creates refund invoice"""
        res = super(account_invoice, self)._refund_cleanup_lines(cr, uid, lines)

        for line in res:
            if 'commission_ids' in line[2]:
                duply_ids = []
                for cm_id in line[2].get('commission_ids', []):
                    dup_id = self.pool['invoice.line.agent'].copy(cr, uid, cm_id, {'settled': False})
                    duply_ids.append(dup_id)
                # line[2]['commission_ids'] = [(6,0, line[2].get('commission_ids', [])) ]
                line[2]['commission_ids'] = [(6, 0, duply_ids)]

        return res

    def invoice_set_agent(self, cr, uid, ids, context=None):
        # this try to set agent on db where module is installed after
        for invoice in self.browse(cr, uid, ids, context):
            vals_line = {}
            if invoice.agent_id:
                vals_line = {
                    'agent_id': invoice.agent_id.id,
                    'commission_id': invoice.agent_id.commission.id
                }
            else:
                for order in invoice.sale_order_ids:
                    section = order.section_id
                    if section and section.sale_agent_id:
                        invoice.write({'section_id': section.id})
                        vals_line = {
                            'agent_id': section.sale_agent_id.id,
                            'commission_id': section.sale_agent_id.commission.id
                        }
                if not vals_line:
                    if invoice.partner_id.section_id and invoice.partner_id.section_id.sale_agent_id:
                        # invoice.write({'section_id': section.id})
                        vals_line = {
                            'agent_id': invoice.partner_id.section_id.sale_agent_id.id,
                            'commission_id': invoice.partner_id.section_id.sale_agent_id.commission.id
                        }

            if vals_line:
                for invoice_line in invoice.invoice_line:
                    # qui devo sistemare tutte le righe
                    if not invoice_line.commission_ids:
                        vals_line.update({'invoice_line_id': invoice_line.id})
                        self.pool['invoice.line.agent'].create(cr, uid, vals_line, context)

    def write(self, cr, uid, ids, values, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        # TODO: set this on a function in workflow, is a wrong mode for call
        state = values.get('state', False)
        if state and state == 'open':
            self.invoice_set_agent(cr, uid, ids, context)

        res = super(account_invoice, self).write(cr, uid, ids, values, context=context)

        return res

