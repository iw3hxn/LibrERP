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
        return self.pool['account.move.line'].search(cr, uid, [('stored_invoice_id', 'in', ids)], context=context)

    def _get_riba_from_payment_term(self, cr, uid, ids, context=None):
        account_invoice_ids = self.pool['account.invoice'].search(cr, uid, [('payment_term', 'in', ids)], context=context)
        return self.pool['account.move.line'].search(cr, uid, [('stored_invoice_id', 'in', account_invoice_ids)], context=context)

    def _set_riba(self, cr, uid, ids, name, value, arg, context=None):
        if not value:
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

    _columns = {
        'distinta_line_ids': fields.one2many('riba.distinta.move.line', 'move_line_id', "Dettaglio riba"),
        'riba': fields.function(_get_fields_riba_function, type='boolean', string='RiBa', fnct_inv=_set_riba, store={
            'account.move.line': (lambda self, cr, uid, ids, c={}: ids, ['stored_invoice_id'], 6000),
            'account.invoice': (_get_riba_from_account_invoice, ['payment_term'], 6000),
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


class account_invoice(orm.Model):
    _inherit = "account.invoice"
    _columns = {
        'unsolved_move_line_ids': fields.many2many('account.move.line', 'invoice_unsolved_line_rel', 'invoice_id', 'line_id', 'Unsolved journal items'),
    }

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
                            account_invoice_line_vals = {
                                'product_id': invoice.payment_term.spese_incasso_id.id,
                                'invoice_id': invoice.id
                            }

                            account_invoice_line_vals.update(account_invoice_line_obj.product_id_change(cr, uid, ids, invoice.payment_term.spese_incasso_id.id, False, type=invoice.type,
                                                           partner_id=invoice.partner_id.id, fposition_id=invoice.fiscal_position and invoice.fiscal_position.id,
                                                           context=context,
                                                           company_id=invoice.company_id.id).get('value'))

                            if account_invoice_line_vals.get('invoice_line_tax_id', False):
                                account_invoice_line_vals['invoice_line_tax_id'] = [(6, False, account_invoice_line_vals.get('invoice_line_tax_id'))]
                            account_invoice_line_vals['quantity'] = len(invoice.payment_term.line_ids)
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
