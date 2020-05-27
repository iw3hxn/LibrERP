# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Andrea Cometa.
#    Email: info@andreacometa.it
#    Web site: http://www.andreacometa.it
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


class account_payment_term(orm.Model):
    # flag riba utile a distinguere la modalità di pagamento
    _inherit = 'account.payment.term'

    _columns = {
        'riba': fields.boolean('Riba'),
        'spese_incasso_id':  fields.many2one('product.product', 'Spese Incasso', domain=[('type', '=', 'service')]),
    }
    _defaults = {
        'riba': False,
    }

    def get_product_incasso(self, cr, uid, context):
        payment_term_obj = self.pool['account.payment.term']

        payment_with_spese_incasso_ids = payment_term_obj.search(cr, uid, [('spese_incasso_id', '!=', False)],
                                                                 context=context)
        excluse_product_ids = [payment.spese_incasso_id.id for payment in
                               payment_term_obj.browse(cr, uid, payment_with_spese_incasso_ids, context)]

        return excluse_product_ids

    def onchange_type(self, cr, uid, ids, type, context=None):
        result = super(account_payment_term, self).onchange_type(cr, uid, ids, type, context)
        if type:
            if type == 'RB':
                result['value']['riba'] = True
            else:
                result['value']['riba'] = False
        return result


class res_bank_add_field(orm.Model):
    _inherit = 'res.bank'
    _columns = {
        'banca_estera': fields.boolean('Banca Estera'),
    }


class res_partner_bank_add(orm.Model):
    _inherit = 'res.partner.bank'
    _columns = {
        'codice_sia': fields.char('Codice SIA', size=5, help="Identification Code of the Company in the System Interbank")
    }


class action_move(orm.Model):
    _inherit = "account.move"

    def button_validate(self, cr, uid, ids, context=None):
        res = super(action_move, self).button_validate(cr, uid, ids, context)
        distinta_line_pool = self.pool['riba.distinta.line']
        invoice_pool = self.pool['account.invoice']
        for move in self.browse(cr, uid, ids, context=context):
            distinta_line_ids = distinta_line_pool.search(cr, uid, [('unsolved_move_id', '=', move.id)], context=context)
            if distinta_line_ids:
                distinta_line = distinta_line_pool.browse(cr, uid, distinta_line_ids[0], context)
                for move_line in move.line_id:
                    account_id = distinta_line.partner_id.property_account_receivable.id
                    fpos = distinta_line.partner_id.property_account_position
                    account_id = self.pool['account.fiscal.position'].map_account(cr, uid, fpos, account_id)
                    if move_line.account_id.id == account_id and move_line.partner_id:  # wizard.over
                        # due_effects_account_id.id:
                        for riba_move_line in distinta_line.move_line_ids:
                            if riba_move_line.move_line_id.invoice:
                                invoice_pool.write(cr, uid, riba_move_line.move_line_id.invoice.id, {
                                    'unsolved_move_line_ids': [(4, move_line.id)],
                                }, context=context)

        return res


# se distinta_line_ids == None allora non è stata emessa
class account_move_line(orm.Model):
    _inherit = "account.move.line"

    def _get_line_values(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'cup': '',
                'cig': '',
            }
            if line.invoice:
                if line.invoice.cig:
                    res[line.id]['cig'] = line.invoice.cig
                if line.invoice.cup:
                    res[line.id]['cup'] = line.invoice.cup
        return res

    def _get_fields_riba_function(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = dict.fromkeys(ids, False)
        for line in self.browse(cr, uid, ids, context):
            if line.stored_invoice_id:
                if line.stored_invoice_id.payment_term:
                    res[line.id] = line.stored_invoice_id.payment_term.riba
        return res

    def _get_riba_from_account_invoice(self, cr, uid, ids, context=None):
        invoice_pool = self.pool['account.invoice']
        res = []
        for invoice in invoice_pool.browse(cr, uid, ids, context=context):
            if invoice.move_id:
                for line in invoice.move_id.line_id:
                    if line.id not in res:
                        res.append(line.id)
        return res

    def _get_riba_from_payment_term(self, cr, uid, ids, context=None):
        account_invoice_ids = self.pool['account.invoice'].search(cr, uid, [('payment_term', 'in', ids)], context=context)
        return self.pool['account.move.line'].search(cr, uid, [('stored_invoice_id', 'in', account_invoice_ids)], context=context)

    def _set_riba(self, cr, uid, ids, name, value, arg, context=None):
        if not name:
            return False
        if isinstance(ids, (int, long)):
            ids = [ids]

        cr.execute("""update account_move_line set
                    riba=%s where id in (%s)""", (value, ', '.join([str(line_id) for line_id in ids])))
        return True

    def _get_invoice(self, cr, uid, ids, field_name, arg, context=None):
        return super(account_move_line, self)._get_invoice(cr, uid, ids, field_name, arg, context)

    def _get_move_lines_riba(self, cr, uid, ids, context=None):
        res = self.pool['account.move.line']._get_move_lines(cr, uid, ids, context)
        for invoice in self.browse(cr, uid, ids, context=context):
            for line in invoice.unsolved_move_line_ids:
                if line.id not in res:
                    res.append(line.id)
        return res

    def _get_riba_bank_id(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, False)
        context['only_iban'] = True

        cr.execute("""SELECT 
                account_move_line.id,
                riba_configurazione.id
            FROM
                public.account_invoice,
                public.account_move_line,
                public.res_partner_bank,
                public.riba_configurazione
            WHERE
                account_move_line.stored_invoice_id = account_invoice.id AND
                res_partner_bank.bank = account_invoice.bank_riba_id AND
                res_partner_bank.partner_id = account_invoice.company_id AND
                riba_configurazione.bank_id = res_partner_bank.id AND
                riba_configurazione.configuration_type = 'supplier' AND
                account_invoice.bank_riba_id IS NOT NULL AND
                account_move_line.id in ({move_ids})
        """.format(move_ids=', '.join([str(move_id) for move_id in ids])))
        val = cr.fetchall()

        for el in val:
            res[el[0]] = el[1]

        return res

    def action_add(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'riba_selected': True}, context)
        return True

    def action_remove(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'riba_selected': False}, context)
        return True

    _columns = {
        'riba_selected': fields.boolean('RiBa Selezionata'),
        'distinta_line_ids': fields.one2many('riba.distinta.move.line', 'move_line_id', "Dettaglio riba"),
        'riba': fields.function(_get_fields_riba_function, type='boolean', string='RiBa', fnct_inv=_set_riba, store={
            'account.move.line': (lambda self, cr, uid, ids, c={}: ids, ['stored_invoice_id'], 6000),
            'account.invoice': (_get_riba_from_account_invoice, ['payment_term', 'move_id'], 6000),
            'account.payment.term': (_get_riba_from_payment_term, ['riba'], 6000),
        }),
        'unsolved_invoice_ids': fields.many2many('account.invoice', 'invoice_unsolved_line_rel', 'line_id', 'invoice_id', 'Unsolved Invoices'),
        'iban': fields.related('partner_id', 'bank_ids', 'iban', type='char', string='IBAN', store=False),
        'abi': fields.related('partner_id', 'bank_riba_id', 'abi', type='char', string='ABI', store=False),
        'cab': fields.related('partner_id', 'bank_riba_id', 'cab', type='char', string='CAB', store=False),
        'cig': fields.function(_get_line_values, string="Cig", type='char', size=64, method=True, multi="line"),
        'cup': fields.function(_get_line_values, string="Cup", type='char', size=64, method=True, multi="line"),
        'stored_invoice_id': fields.function(_get_invoice, method=True, string="Invoice", type="many2one", relation="account.invoice",
                                             store={
                                                 'account.move.line': (lambda self, cr, uid, ids, c={}: ids, ['move_id'], 10),
                                                 'account.invoice': (_get_move_lines_riba, ['move_id', 'unsolved_move_line_ids'], 10),
                                             }),
        'riba_bank_id': fields.function(_get_riba_bank_id, method=True, string="Bank Ri.Ba.", type="many2one", relation="riba.configurazione",
                                        store={
                                            'account.move.line': (lambda self, cr, uid, ids, c={}: ids, ['move_id'], 7000),
                                            'account.invoice': (_get_move_lines_riba, ['payment_term', 'bank_riba_id'], 7000),
                                            'account.payment.term': (_get_riba_from_payment_term, ['riba'], 7000),
                                        }),
    }
    _defaults = {
        'distinta_line_ids': None,
    }

    def _hook_get_invoice_line(self, cr, uid, line, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        invoice_pool = self.pool['account.invoice']
        res = invoice_pool.search(cr, 1, [('unsolved_move_line_ids', '=', line.id)], context=context)
        if res:
            return res[0]
        else:
            return super(account_move_line, self)._hook_get_invoice_line(cr, uid, line, context)

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context={}, toolbar=False, submenu=False):
        view_payments_tree_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'l10n_it_ricevute_bancarie', 'view_riba_da_emettere_tree')
        if view_id == view_payments_tree_id[1]:
            # Use RiBa list - grazie a eLBati @ account_due_list
            result = super(orm.Model, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        else:
            # Use special views for account.move.line object (for ex. tree view contains user defined fields)
            result = super(account_move_line, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        return result

    def unlink(self, cr, uid, ids, context=None, check=True):
        if not context:
            context = {}
        riba_distinta_line_obj = self.pool['riba.distinta.line']
        riba_distinta_move_line_obj = self.pool['riba.distinta.move.line']
        riba_distinta_move_line_ids = riba_distinta_move_line_obj.search(cr, uid, [('move_line_id', 'in', ids)], context=context)
        if riba_distinta_move_line_ids:
            riba_line_ids = riba_distinta_line_obj.search(cr, uid, [('move_line_ids', 'in', riba_distinta_move_line_ids)], context=context)
            if riba_line_ids:
                for riba_line in riba_distinta_line_obj.browse(cr, uid, riba_line_ids, context=context):
                    if riba_line.state in ['draft', 'cancel']:
                        riba_distinta_line_obj.unlink(cr, uid, riba_line_ids, context=context)
                        # TODO: unlink in 'accepted' state too?
        return super(account_move_line, self).unlink(cr, uid, ids, context=context, check=check)

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not order and context.get('order', False):
            order = context['order']
        res = super(account_move_line, self).search(cr, uid, args, offset, limit, order, context, count)
        return res


class account_invoice(orm.Model):
    _inherit = "account.invoice"
    _columns = {
        'unsolved_move_line_ids': fields.many2many('account.move.line', 'invoice_unsolved_line_rel', 'invoice_id', 'line_id', 'Unsolved journal items'),
    }

    def merge_invoice(self, cr, uid, invoices, merge_lines, context=None):
        invoice_id = super(account_invoice, self).merge_invoice(cr, uid, invoices, merge_lines, context)
        product_exclude_ids = self.pool['account.payment.term'].get_product_incasso(cr, uid, context)
        account_invoice_line_obj = self.pool['account.invoice.line']
        line_to_delete_ids = account_invoice_line_obj.search(cr, uid, [('invoice_id', '=', invoice_id), ('product_id', 'in', product_exclude_ids)], context=context)
        if line_to_delete_ids:
            account_invoice_line_obj.unlink(cr, uid, line_to_delete_ids, context)
            self.button_reset_taxes(cr, uid, [invoice_id], context)
        return invoice_id

    def _spese_incasso_vals(self, cr, uid, ids, spese_incasso_id, invoice_id, invoice_type, partner_id, company_id, payment_term_id, fiscal_position_id=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        account_invoice_line_obj = self.pool['account.invoice.line']
        account_invoice_line_vals = {
            'product_id': spese_incasso_id,
        }
        if invoice_id:
            account_invoice_line_vals.update(invoice_id=invoice_id)
        account_invoice_line_vals.update(
            account_invoice_line_obj.product_id_change(cr, uid, ids, spese_incasso_id, False,
                                                       type=invoice_type,
                                                       partner_id=partner_id,
                                                       fposition_id=fiscal_position_id,
                                                       context=context,
                                                       company_id=company_id).get('value'))

        if account_invoice_line_vals.get('invoice_line_tax_id', False):
            account_invoice_line_vals['invoice_line_tax_id'] = [(6, False, account_invoice_line_vals.get('invoice_line_tax_id'))]

        quantity = len(self.pool['account.payment.term'].read(cr, uid, payment_term_id, ['line_ids'], context=context)['line_ids'])
        account_invoice_line_vals['quantity'] = quantity
        return account_invoice_line_vals

    def onchange_payment_term(self, cr, uid, ids, partner_id, payment_term_id, invoice_line, fiscal_position_id, company_id, invoice_type, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {'value': {}}
        if payment_term_id and invoice_line:
            payment_term_obj = self.pool['account.payment.term']
            account_invoice_line_obj = self.pool['account.invoice.line']
            payment_with_spese_incasso_ids = payment_term_obj.search(cr, uid, [('spese_incasso_id', '!=', False)], context=context)
            product_spese_incasso_ids = [payment.spese_incasso_id.id for payment in payment_term_obj.browse(cr, uid, payment_with_spese_incasso_ids, context)]

            invoice_line_ids = []

            for line in invoice_line:
                if line[0] == 4:
                    invoice_line_ids.append(line[1])

            if invoice_line_ids:
                account_invoice_line_ids = account_invoice_line_obj.search(cr, uid, [('id', 'in', invoice_line_ids), ('product_id', 'in', product_spese_incasso_ids)], context=context)
            else:
                account_invoice_line_ids = []

            new_invoice_line = []
            for line in invoice_line:
                if line[0] == 4:
                    if line[1] in account_invoice_line_ids:
                        new_invoice_line.append([2, line[1], False])
                        continue
                if line[0] == 0 or line[0] == 1:
                    if 'product_id' in line[2] and line[2]['product_id'] in product_spese_incasso_ids:
                        continue

                new_invoice_line.append(line)

            spese_incasso_id = payment_term_obj.read(cr, uid, payment_term_id, ['spese_incasso_id'], context=context, load='_obj')['spese_incasso_id']

            if spese_incasso_id:
                account_invoice_line_vals = self._spese_incasso_vals(
                    cr, uid, ids, spese_incasso_id, invoice_id=False,
                    invoice_type=invoice_type, partner_id=partner_id,
                    company_id=company_id, payment_term_id=payment_term_id,
                    fiscal_position_id=fiscal_position_id, context=context
                )
                new_invoice_line.append([0, 0, account_invoice_line_vals])

            res['value']['invoice_line'] = new_invoice_line

        return res

    def invoice_validate_check(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(account_invoice, self).invoice_validate_check(cr, uid, ids, context)
        show_except = not context.get('no_except', False)
        if not res:
            return False
        else:
            for invoice in self.browse(cr, uid, ids, context):
                if invoice.type == 'out_invoice' and invoice.payment_term:
                    if invoice.payment_term.spese_incasso_id:
                        account_invoice_line_obj = self.pool['account.invoice.line']
                        account_invoice_line_ids = account_invoice_line_obj.search(cr, uid, [('product_id', '=', invoice.payment_term.spese_incasso_id.id), ('invoice_id', '=', invoice.id)], context=context)
                        if not account_invoice_line_ids:
                            # i have to add spese incasso
                            fiscal_position_id = invoice.fiscal_position and invoice.fiscal_position.id
                            account_invoice_line_vals = self._spese_incasso_vals(
                                cr, uid, ids, invoice.payment_term.spese_incasso_id.id, invoice.id, invoice.type,
                                invoice.partner_id.id, invoice.company_id.id, invoice.payment_term.id,
                                fiscal_position_id, context=context)
                            account_invoice_line_obj.create(cr, uid, account_invoice_line_vals, context)
                            invoice.button_compute()

                    if invoice.payment_term.riba and invoice.type == 'out_invoice':
                        if not invoice.partner_id.bank_riba_id:
                            if show_except:
                                raise orm.except_orm(u'Fattura Cliente',
                                   u'Impossibile da validare in quanto non è impostata la banca appoggio Riba nel partner {partner}'.format(partner=invoice.partner_id.name))
                            else:
                                return False
                        if not invoice.partner_id.bank_riba_id.abi or not invoice.partner_id.bank_riba_id.cab:
                            if show_except:
                                raise orm.except_orm(u'Fattura Cliente',
                                   u'Impossibile da validare in quanto non è impostata ABI o CAB nella fattura di {partner}'.format(partner=invoice.partner_id.name))
                            else:
                                return False

        return True

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res_bank_obj = self.pool['res.bank']
        result = super(account_invoice, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and context.get('type', False) == 'in_invoice':
            if result['fields'].get('bank_riba_id', False):
                company_id = self.pool['res.users'].browse(cr, uid, uid, context).company_id.id
                cr.execute("select bank from res_partner_bank where company_id = {company_id}".format(company_id=company_id))
                bank_ids = []
                for rec in cr.fetchall():
                    bank_ids.append(rec[0])
                result['fields']['bank_riba_id']['domain'] = [('id', 'in', bank_ids)]
                result['fields']['bank_riba_id']['selection'] = res_bank_obj.name_search(cr, uid, '', [('id', 'in', bank_ids)], context=context)

        return result

    def onchange_partner_id(self, cr, uid, ids, i_type, partner_id, date_invoice=False, payment_term=False, bank_riba_id=False, company_id=False, context=None):
        result = super(account_invoice, self).onchange_partner_id(
            cr, uid, ids, i_type, partner_id, date_invoice, payment_term, bank_riba_id, company_id)

        if i_type in ['in_invoice']:
            partner = self.pool['res.partner'].browse(cr, uid, partner_id, context)
            if partner.company_riba_bank_id and partner.company_riba_bank_id.bank:
                result['value']['bank_riba_id'] = partner.company_riba_bank_id.bank.id

        return result
