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

"""Modificamos la creación de factura desde albarán para incluir el comportamiento de comisiones"""

from openerp.osv import orm, fields


class stock_picking(orm.Model):
    """Modificamos la creación de factura desde albarán para incluir el comportamiento de comisiones"""

    _inherit = 'stock.picking'

    _columns = {
        'agent_ids': fields.many2many('sale.agent', 'sale_agent_clinic_rel', 'agent_id', 'clinic_id', 'Agentes')
    }

    def _create_invoice_line_agent(self, cr, uid, ids, agent_id, commission_id, invoice_line_id):
        vals = {
            'agent_id': agent_id,
            'commission_id': commission_id,
            'settled': False,
            'invoice_line_id': invoice_line_id
        }
        line_agent_id = self.pool['invoice.line.agent'].create(cr, uid, vals)
        self.pool['invoice.line.agent'].calculate_commission(cr, uid, [line_agent_id])
        return line_agent_id

    def _invoice_hook(self, cr, uid, picking, invoice_id):
        '''Call after the creation of the invoice'''
        super(stock_picking, self)._invoice_hook(cr, uid, picking, invoice_id)

        if picking.sale_id and picking.sale_id.section_id:
            self.pool['account.invoice'].write(cr, uid, [int(invoice_id)], {'section_id': picking.sale_id.section_id.id})
        else:
            self.pool['account.invoice'].browse(cr, uid, int(invoice_id))
            invoice = self.pool['account.invoice'].browse(cr, uid, int(invoice_id))
            partner_section = invoice.section_id and invoice.section_id.id
            if partner_section:
                invoice.write({'section_id': partner_section})
        return

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        '''Call after the creation of the invoice line'''
        super(stock_picking, self)._invoice_line_hook(cr, uid, move_line, invoice_line_id)

        if move_line and move_line.sale_line_id and move_line.sale_line_id.product_id.commission_exent != True:
            so_ref = move_line.sale_line_id.order_id
            line = move_line.sale_line_id
            if not line.line_agent_ids:
                for so_comm in line.order_id.sale_agent_ids:
                    line_agent_id = self._create_invoice_line_agent(cr, uid, [], so_comm.agent_id.id,
                                                                    so_comm.commission_id.id, invoice_line_id)
            else:
                for l_comm in line.line_agent_ids:
                    line_agent_id = self._create_invoice_line_agent(cr, uid, [], l_comm.agent_id.id,
                                                                    l_comm.commission_id.id, invoice_line_id)
        return
