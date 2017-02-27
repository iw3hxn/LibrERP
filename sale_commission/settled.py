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

"""Objetos sobre las liquidación"""

from openerp.osv import orm, fields
from tools.translate import _
import time
import tools
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class recalculate_commision_wizard(orm.TransientModel):
    """settled.wizard"""

    _name = 'recalculate.commission.wizard'
    _columns = {
        'date_from': fields.date('From', required=True),
        'date_to': fields.date('To', required=True),
    }
    _defaults = {
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def recalculate_exec(self, cr, uid, ids, context=None):
        """se ejecuta correctamente desde dos."""
        company_id = self.pool['res.users']._get_company(cr, uid, context)
        invoice_obj = self.pool['account.invoice']

        for o in self.browse(cr, uid, ids, context=context):
            # quasi quasi qui farei un ricalcolo delle fatture

            invoice_ids = invoice_obj.search(cr, uid, [('date_invoice', '>=', o.date_from), ('date_invoice', '<=', o.date_to)])
            invoice_obj.invoice_set_agent(cr, uid, invoice_ids, context)

            sql = 'SELECT  invoice_line_agent.id FROM account_invoice_line ' \
                  'INNER JOIN invoice_line_agent ON invoice_line_agent.invoice_line_id=account_invoice_line.id ' \
                  'INNER JOIN account_invoice ON account_invoice_line.invoice_id = account_invoice.id ' \
                  'WHERE invoice_line_agent.agent_id in (' + ",".join(
                map(str, context['active_ids'])) + ') AND invoice_line_agent.settled=False ' \
                                                   'AND account_invoice.state not in (\'draft\',\'cancel\') AND account_invoice.type in (\'out_invoice\',\'out_refund\')' \
                                                   'AND account_invoice.date_invoice >= \'' + o.date_from + '\' AND account_invoice.date_invoice <= \'' + o.date_to + '\'' \
                                                   ' AND account_invoice.company_id = ' + str(company_id)

            cr.execute(sql)
            res = cr.fetchall()
            inv_line_agent_ids = [x[0] for x in res]
            self.pool['invoice.line.agent'].calculate_commission(cr, uid, inv_line_agent_ids)

        return {
            'type': 'ir.actions.act_window_close',
        }

    def action_cancel(self, cr, uid, ids, conect=None):
        """CANCEL CALCULATE"""
        return {
            'type': 'ir.actions.act_window_close',
        }


class settlement(orm.Model):
    """Objeto Liquidación"""

    _name = 'settlement'
    _columns = {
        'name': fields.char('Settlement period', size=64, required=True, readonly=True),
        'total': fields.float('Total', readonly=True),
        'date_from': fields.date('From'),
        'date_to': fields.date('To'),
        'settlement_agent_id': fields.one2many('settlement.agent', 'settlement_id', 'Settlement agents', readonly=True),
        'date': fields.datetime('Created Date', required=True),
        'state': fields.selection([('invoiced', 'Invoiced'), ('settled', 'Settled'), ('cancel', 'Cancel')], 'State',
                                  required=True, readonly=True)
    }
    _defaults = {
        'date': lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'state': lambda *a: 'settled'
    }

    def write(self, cr, uid, ids, vals, context=None):

        if vals.get('date_from', False) or vals.get('date_to', False):

            for o in self.browse(cr, uid, ids, context=context):
                name = vals.get('date_from', o.date_from) + " <=> " + vals.get('date_to', o.date_to)
            vals.update({'name': name})

        return super(settlement, self).write(cr, uid, ids, vals, context=context)

    def action_invoice_create(self, cursor, user, ids, journal_id, product_id, mode, context=None):

        agents_pool = self.pool['settlement.agent']
        res = {}
        for settlement in self.browse(cursor, user, ids, context=context):
            settlement_agent_ids = map(lambda x: x.id, settlement.settlement_agent_id)
            invoices_agent = agents_pool.action_invoice_create(cursor, user, settlement_agent_ids, journal_id,
                                                               product_id, mode)

            res[settlement.id] = invoices_agent.values()
        return res

    def calcula(self, cr, uid, liq_id, agent_ids, date_from, date_to):
        """genera una entrada de liquidación por agente"""

        context = self.pool['res.users'].context_get(cr, uid)
        # Search all lines settlement invoiced in a period
        agents = self.pool['sale.agent'].browse(cr, uid, agent_ids, context)
        total = 0

        for agent in agents:
            # genera una entrada de liquidación por agente
            liq_agent_id = self.pool['settlement.agent'].create(cr, uid,
                                                                {'agent_id': agent.id, 'settlement_id': liq_id},
                                                                context)
            self.pool['settlement.agent'].calcula(cr, uid, liq_agent_id, date_from, date_to)
            liq_agent = self.pool['settlement.agent'].browse(cr, uid, liq_agent_id, context)
            total = total + liq_agent.total

        return self.write(cr, uid, liq_id, {'total': total}, context)

    def action_cancel(self, cr, uid, ids, context=None):
        """Cancela la liquidación"""
        if context is None:
            context = {}
        for settle in self.browse(cr, uid, ids, context):
            for settle_line in settle.settlement_agent_id:
                for line in settle_line.lines:
                    commission_ids = line.invoice_line_id and [x.id for x in line.invoice_line_id.commission_ids] or []
                    if commission_ids:
                        self.pool['invoice.line.agent'].write(cr, uid, commission_ids,
                                                              {'settled': False, 'quantity': 0.0}, context)

        return self.write(cr, uid, ids, {'state': 'cancel'}, context)

    def unlink(self, cr, uid, ids, context=None):
        """permite borrar liquidaciones canceladas"""
        for settle in self.browse(cr, uid, ids, context):
            if settle.state != 'cancel':
                raise orm.except_orm(_('Error!'), _("You can\'t delete it, if it isn't in cancel state."))

        return super(settlement, self).unlink(cr, uid, ids, context=context)


class settlement_agent(orm.Model):
    """Liquidaciones de Agentes"""

    _name = 'settlement.agent'
    _rec_name = 'agent_id'

    # def _invoice_line_hook(self, cursor, user, move_line, invoice_line_id):
    #     '''Call after the creation of the invoice line'''
    #     return
    #
    # def _invoice_hook(self, cursor, user, picking, invoice_id):
    #     '''Call after the creation of the invoice'''
    #     return

    def _get_address_invoice(self, cursor, user, settlement):
        '''Return {'contact': address, 'invoice': address} for invoice'''
        partner = settlement.agent_id.partner_id

        return self.pool['res.partner'].address_get(cursor, user, [partner.id],
                                                    ['contact', 'invoice'])

    _columns = {
        'agent_id': fields.many2one('sale.agent', 'Agent', required=True, select=1),
        'total_per': fields.float('Total percentages', readonly=True),
        'total_sections': fields.float('Total sections', readonly=True),
        'total': fields.float('Total', readonly=True),
        'lines': fields.one2many('settlement.line', 'settlement_agent_id', 'Lines', readonly=True),
        'invoices': fields.one2many('settled.invoice.agent', 'settlement_agent_id', 'Invoices', readonly=True),
        'settlement_id': fields.many2one('settlement', 'Settlement', required=True, ondelete="cascade")
    }

    def get_currency_id(self, cursor, user, picking):
        return False

    def action_invoice_create(self, cr, uid, ids, journal_id, product_id, mode, context=None):
        '''Return ids of created invoices for the settlements'''

        invoice_obj = self.pool['account.invoice']
        invoice_line_obj = self.pool['account.invoice.line']
        invoices_group = {}
        res = {}

        for settlement in self.browse(cr, uid, ids, context=context):
            if (not settlement.total_sections) and (not settlement.total):
                continue
            payment_term_id = False
            partner = settlement.agent_id and settlement.agent_id.partner_id
            if not partner:
                continue
                # El tipo es de facura de proveedor
            account_id = partner.property_account_payable.id

            address_contact_id, address_invoice_id = \
                self._get_address_invoice(cr, uid, settlement).values()

            # No se agrupa

            invoice_vals = {
                'name': settlement.settlement_id.name,
                'origin': (settlement.settlement_id.name or ''),
                'type': 'in_invoice',
                'account_id': account_id,
                'partner_id': partner.id,
                'address_invoice_id': address_invoice_id,
                'address_contact_id': address_contact_id,
                # 'comment': comment,
                'payment_term': payment_term_id,
                'fiscal_position': partner.property_account_position.id
            }
            cur_id = self.get_currency_id(cr, uid, settlement)
            if cur_id:
                invoice_vals['currency_id'] = cur_id
            if journal_id:
                invoice_vals['journal_id'] = journal_id

            invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)

            res[settlement.id] = invoice_id
            # El producto se selecciona en el wizard correspondiente
            product = self.pool['product.product'].browse(cr, uid, product_id, context)
            account_id = product.product_tmpl_id.property_account_expense.id
            if not account_id:
                account_id = product.categ_id.property_account_expense_categ.id
            # Cálculo de los impuestos a aplicar

            taxes = product.supplier_taxes_id

            if settlement.agent_id and settlement.agent_id.partner_id:
                tax_ids = self.pool['account.fiscal.position'].map_tax(
                    cr,
                    uid,
                    settlement.agent_id.partner_id.property_account_position,
                    taxes
                )
            else:
                tax_ids = map(lambda x: x.id, taxes)

            account_id = self.pool['account.fiscal.position'].map_account(cr, uid, partner.property_account_position,
                                                                          account_id)
            uos_id = False  # set UoS if it's a sale and the picking doesn't have one
            if mode == 'invoice':
                for invoice in settlement.invoices:
                    invoice_line_id = invoice_line_obj.create(cr, uid, {
                        'name': invoice.invoice_number,
                        'origin': invoice.invoice_number,
                        'invoice_id': invoice_id,
                        'uos_id': uos_id,
                        'product_id': product.id,
                        'account_id': account_id,
                        'price_unit': invoice.settled_amount,
                        'discount': 0,
                        'quantity': 1,
                        'invoice_line_tax_id': [(6, 0, tax_ids)],
                    }, context=context)
            elif mode == 'line':
                for line in settlement.lines:
                    invoice_line_id = invoice_line_obj.create(cr, uid, {
                        'name': line.invoice_id.number,
                        'origin': line.invoice_id.number,
                        'invoice_id': invoice_id,
                        'uos_id': uos_id,
                        'product_id': product.id,
                        'account_id': account_id,
                        'price_unit': line.commission,
                        'discount': 0,
                        'quantity': 1,
                        'invoice_line_tax_id': [(6, 0, tax_ids)],
                    }, context=context)
            elif mode == 'agent':
                invoice_line_id = invoice_line_obj.create(cr, uid, {
                    'name': settlement.settlement_id.name or '',
                    'origin': settlement.settlement_id.name or '',
                    'invoice_id': invoice_id,
                    'uos_id': uos_id,
                    'product_id': product.id,
                    'account_id': account_id,
                    'price_unit': settlement.total,
                    'discount': 0,
                    'quantity': 1,
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                }, context=context)

            invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
                                       set_total=(type in ('in_invoice', 'in_refund')))

            self._invoice_hook(cr, uid, settlement, invoice_id)
        return res

    def calcula(self, cr, uid, ids, date_from, date_to):

        context = self.pool['res.users'].context_get(cr, uid)
        settlement_line_pool = self.pool['settlement.line']
        invoice_line_agent_pool = self.pool['invoice.line.agent']
        set_agent = self.browse(cr, uid, ids, context)
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        # Recalculamos todas las lineas sujetas a comision
        sql = """
              SELECT  invoice_line_agent.id FROM account_invoice_line
              INNER JOIN invoice_line_agent ON invoice_line_agent.invoice_line_id=account_invoice_line.id
              INNER JOIN account_invoice ON account_invoice_line.invoice_id = account_invoice.id
              WHERE invoice_line_agent.agent_id= {agent_id}
              AND invoice_line_agent.settled = True
              AND account_invoice.state in ('open', 'paid') AND account_invoice.type in ('out_invoice', 'out_refund')
              AND account_invoice.date_invoice >= '{date_from}'
              AND account_invoice.date_invoice <= '{date_to}'
              AND account_invoice.company_id = {company_id}
              """.format(agent_id=set_agent.agent_id.id, date_from=date_from, date_to=date_to, company_id=user.company_id.id)
        cr.execute(sql)
        res = cr.fetchall()
        inv_line_agent_ids = [x[0] for x in res]
        invoice_line_agent_pool.calculate_commission(cr, uid, inv_line_agent_ids, context=context)
        sql = """
              SELECT  account_invoice_line.id FROM account_invoice_line
              INNER JOIN invoice_line_agent ON invoice_line_agent.invoice_line_id=account_invoice_line.id
              INNER JOIN account_invoice ON account_invoice_line.invoice_id = account_invoice.id
              WHERE invoice_line_agent.agent_id = {agent_id}
              AND invoice_line_agent.settled = False
              AND account_invoice.state in ('open', 'paid') AND account_invoice.type in ('out_invoice', 'out_refund')
              AND account_invoice.date_invoice >= '{date_from}'
              AND account_invoice.date_invoice <= '{date_to}'
              AND account_invoice.company_id = {company_id}
              """.format(agent_id=set_agent.agent_id.id, date_from=date_from, date_to=date_to, company_id=user.company_id.id)
        cr.execute(sql)
        res = cr.fetchall()
        inv_line_ids = [x[0] for x in res]
        total_per = 0
        total_sections = 0
        sections = {}
        for inv_line_id in inv_line_ids:
            linea_id = self.pool['settlement.line'].create(cr, uid,
                                                           {'invoice_line_id': inv_line_id, 'settlement_agent_id': ids})
            self.pool['settlement.line'].calcula(cr, uid, linea_id)

            line = self.pool['settlement.line'].browse(cr, uid, linea_id)

            # Marca la comision en la factura como liquidada y establece la cantidad
            # Si es por tramos la cantidad será cero, pero se reflejará sobre el section del Agente

            if line.commission_id.type == "fix":
                total_per = total_per + line.commission
                inv_ag_ids = self.pool['invoice.line.agent'].search(cr, uid, [('invoice_line_id', '=', inv_line_id),
                                                                              ('agent_id', '=', set_agent.agent_id.id)], context=context)
                self.pool['invoice.line.agent'].write(cr, uid, inv_ag_ids,
                                                      {'settled': True, 'quantity': line.commission}, context=context)
            if line.commission_id.type == "sections":
                if line.invoice_line_id.product_id.commission_exent != True:
                    # Hacemos un agregado de la base de cálculo agrupándolo por las distintas comisiones en tramos que tenga el agente asignadas
                    if line.invoice_line_id.invoice_id.type == 'out_refund':
                        sign_price = - line.invoice_line_id.price_subtotal
                    else:
                        sign_price = line.invoice_line_id.price_subtotal

                    if line.commission_id.id in sections:
                        sections[line.commission_id.id]['base'] = sections[line.commission_id.id]['base'] + sign_price
                        sections[line.commission_id.id]['lines'].append(line)  # Añade la línea de la que se añade esta base para el cálculo por tramos
                    else:
                        sections[line.commission_id.id] = {'type': line.commission_id, 'base': sign_price,
                                                           'lines': [line]}
        # Tramos para cada tipo de comisión creados
        for section in sections:
            # Cálculo de la comisión  para cada section
            sections[section].update({'commission': sections[section]['type'].calculate_sections(sections[section]['base'])})
            total_sections = total_sections + sections[section]['commission']
            # reparto de la comisión para cada linea

            for line_section in sections[section]['lines']:
                com_por_linea = sections[section]['commission'] * (
                    line_section.invoice_line_id.price_subtotal / (abs(sections[section]['base']) or 1.0))
                line_section.write({'commission': com_por_linea}, context)
                inv_ag_ids = self.pool['invoice.line.agent'].search(cr, uid, [
                    ('invoice_line_id', '=', line_section.invoice_line_id.id),
                    ('agent_id', '=', set_agent.agent_id.id)], context=context)
                self.pool['invoice.line.agent'].write(cr, uid, inv_ag_ids, {'settled': True, 'quantity': com_por_linea}, context)

        total = total_per + total_sections
        self.write(cr, uid, ids, {'total_per': total_per, 'total_sections': total_sections, 'total': total}, context)


class settlement_line(orm.Model):
    """Línea de las liquidaciones de los agentes
     Una línea por línea de factura
    """

    _name = 'settlement.line'
    _columns = {
        'invoice_id': fields.related('invoice_line_id', 'invoice_id', type='many2one', relation='account.invoice',
                                     string='Invoice'),
        'partner_id': fields.related('invoice_id', 'partner_id', type='many2one', relation='res.partner',
                                     string='Partner'),
        'invoice_date': fields.related('invoice_id', 'date_invoice', type='date', readonly=True, string='Invoice Date'),
        'settlement_agent_id': fields.many2one('settlement.agent', 'Settlement agent', required=True, select=1,
                                               ondelete="cascade"),
        'invoice_line_id': fields.many2one('account.invoice.line', 'Settled invoice line', required=True),
        'amount': fields.float('Invoice line amount', readonly=True),
        'currency_id': fields.many2one('res.currency', 'Currency', readonly=True),
        'commission_id': fields.many2one('commission', 'Commission', readonly=True),
        'commission': fields.float('Quantity', readonly=True),
    }

    _defaults = {
        'currency_id': lambda self, cr, uid, context: self.pool['res.users'].browse(cr, uid, uid,
                                                                                    context).company_id.currency_id.id
    }

    def calcula(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids, context)
        amount = 0
        user = self.pool['res.users'].browse(cr, uid, uid, context)

        for commission in line.invoice_line_id.commission_ids:  # Recorre los agentes y condiciones asignados a la factura
            if commission.agent_id.id == line.settlement_agent_id.agent_id.id:  # selecciona el asignado al agente para el que está liquidando
                commission_app = commission.commission_id  # Obtiene el objeto
                invoice_line_amount = line.invoice_line_id.price_subtotal
                if commission_app.type == "fix":
                    commission_per = commission_app.fix_qty
                    datas_commission_ids = self.pool['hr.agent.commission'].search(cr, uid, [('commission_id', '=', commission_app.id)], context=context)
                    # Para tener en cuenta las rectificativas
                    if datas_commission_ids:
                        for data_commission in self.pool['hr.agent.commission'].browse(cr, uid, datas_commission_ids, context):
                            commission_percent = 0.0
                            fixed_commission = 0.0
                            if line.invoice_line_id.product_id:
                                if line.invoice_line_id.product_id.categ_id == data_commission.category_id:
                                    commission_percent = float(data_commission.commission_percent)
                                    fixed_commission = float(data_commission.fixed_commission)
                                    break
                                elif line.invoice_line_id.product_id == data_commission.product_id:
                                    commission_percent = float(data_commission.commission_percent)
                                    fixed_commission = float(data_commission.fixed_commission)
                                    break
                            if line.invoice_id.partner_id == data_commission.customer_id:
                                commission_percent = float(data_commission.commission_percent)
                                fixed_commission = float(data_commission.fixed_commission)
                                break

                        if not (commission_percent or fixed_commission):
                            commission_percent = commission_per
                        commission = (line.invoice_line_id.price_subtotal * float(commission_percent) / 100) + (float(fixed_commission) * line.invoice_line_id.quantity)

                        if line.invoice_line_id.invoice_id.type == 'out_refund':
                            amount -= commission
                        else:
                            amount += commission
                    else:
                        if line.invoice_line_id.invoice_id.type == 'out_refund':
                            amount -= line.invoice_line_id.price_subtotal * float(commission_per) / 100
                        else:
                            amount += line.invoice_line_id.price_subtotal * float(commission_per) / 100

                elif commission_app.type == "sections":
                    invoice_line_amount = 0
                    amount = 0

                cc_amount_subtotal = line.invoice_id.currency_id.id != user.company_id.currency_id.id and self.pool.get(
                    'res.currency').compute(cr, uid, line.invoice_id.currency_id.id, user.company_id.currency_id.id,
                                            invoice_line_amount, round=False) or invoice_line_amount
                cc_commission_amount = line.invoice_id.currency_id.id != user.company_id.currency_id.id and self.pool.get(
                    'res.currency').compute(cr, uid, line.invoice_id.currency_id.id, user.company_id.currency_id.id,
                                            amount, round=False) or amount

                self.write(cr, uid, ids, {'amount': cc_amount_subtotal, 'commission_id': commission_app.id,
                                          'commission': cc_commission_amount,
                                          'currency_id': user.company_id.currency_id.id})


class settled_invoice_agent(orm.Model):
    _name = 'settled.invoice.agent'
    _description = "Resumen de facturas liquidadas"
    _auto = False
    _columns = {
        'agent_id': fields.many2one('sale.agent', 'Agent', readonly=True, select=1),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, select=1),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True, select=1),
        'settlement_agent_id': fields.many2one('settlement.agent', 'Agent settl.', readonly=True, select=1,
                                               ondelete="cascade"),
        'invoice_number': fields.related('invoice_id', 'number', type='char', string='Invoice no', readonly=True),
        'invoice_date': fields.related('invoice_id', 'date_invoice', string='Invoice date', type='date', readonly=True,
                                       select=1),
        'invoice_amount': fields.float('Amount assigned in invoice', readonly=True),
        'settled_amount': fields.float('Settled amount', readonly=True),
        # 'currency_id': fields.many2one('res.currency', 'Currency', readonly=True, select="1")
    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, "settled_invoice_agent")

        cr.execute("""
            create or replace view settled_invoice_agent as (
            SELECT  (account_invoice_line.invoice_id*10000+settlement_agent.agent_id) as id, settlement_agent.id as settlement_agent_id,
            account_invoice_line.invoice_id as invoice_id, settlement_agent.agent_id as agent_id, MAX(account_invoice.partner_id) as partner_id,
            sum(settlement_line.amount) as invoice_amount,
            sum(settlement_line.commission) as settled_amount
            FROM settlement_agent
              INNER JOIN settlement_line ON settlement_agent.id = settlement_line.settlement_agent_id
              INNER JOIN account_invoice_line ON account_invoice_line.id = settlement_line.invoice_line_id
              INNER JOIN account_invoice ON account_invoice.id = account_invoice_line.invoice_id
              GROUP BY account_invoice_line.invoice_id, settlement_agent.agent_id, settlement_agent.id

           )""")
