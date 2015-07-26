# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2013 Associazione OpenERP Italia
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

from openerp.report import report_sxw
from openerp.tools.translate import _
import logging
from datetime import datetime
from openerp.osv import fields, orm

_logger = logging.getLogger(__name__)


class Parser(report_sxw.rml_parse):

    def _get_account_lines(self, move):
        res = []
        #tax_code_obj = self.pool.get('account.tax.code')
        # index è usato per non ripetere la stampa dei dati fattura quando ci sono più codici IVA
        index = 0
        invoice = False
        for move_line in move.line_id:
            if move_line.invoice:
                if invoice and invoice.id != move_line.invoice.id:
                    raise Exception(_("Move %s contains different invoices") % move.name)
                invoice = move_line.invoice
            account_item = {
                'tax_code_name': move_line.tax_code_id.name,
                'amount': move_line.tax_amount,
                'account_name': move_line.account_id.name,
                'index': index,
                'ref': move_line.ref,
                'invoice_date': (invoice and invoice.date_invoice or move.date or ''),
                'supplier_invoice_number': (invoice and invoice.supplier_invoice_number or ''),
                'amount_total': invoice and invoice.amount_total or '',
            }
            res.append(account_item)
            #index += 1
        return res

    def _tax_amounts_by_code(self, move):
        res = {}
        result = {}
#prima creare solo le righe con l'imponibile
        for move_line in move.line_id:
            if move_line.tax_code_id and not move_line.tax_code_id.exclude_from_registries:
                if not res.get(move_line.tax_code_id.id):
                    res[move_line.tax_code_id.id] = 0.0
                    self.localcontext['used_tax_codes'][move_line.tax_code_id.id] = True
                if move_line.tax_code_id.is_base:
                    amount = (move_line.tax_amount * self.localcontext['data']['tax_sign'])
                    if result.has_key(move_line.tax_code_id.id):
                        result[move_line.tax_code_id.id]['base'] += amount
                    else:
                        result[move_line.tax_code_id.id] = {'base': amount, 'tax': 0.0}

#quindi aggiungere la tax se c'è
        for move_line in move.line_id:
            tax_code = False
            if move_line.tax_code_id and not move_line.tax_code_id.exclude_from_registries:
                
                if not move_line.tax_code_id.is_base:
                    #if move_line.tax_code_id.tax_ids:
                    if move_line.tax_code_id.tax_ids[0].base_code_id:
                        tax_code = move_line.tax_code_id.tax_ids[0].base_code_id
                    #elif move_line.tax_code_id.ref_tax_ids:
                    elif move_line.tax_code_id.ref_tax_ids[0].ref_base_code_id:
                        tax_code = move_line.tax_code_id.ref_tax_ids[0].ref_tax_code_id
                    else:
                        if move_line.tax_code_id.tax_ids:
                            if move_line.tax_code_id.tax_ids[0].parent_id.base_code_id:
                                tax_code = move_line.tax_code_id.tax_ids[0].parent_id.base_code_id
                        elif move_line.tax_code_id.ref_tax_ids:
                            if move_line.tax_code_id.ref_tax_ids[0].parent_id.ref_base_code_id:
                                tax_code = move_line.tax_code_id.ref_tax_ids[0].parent_id.ref_tax_code_id
                        else:
                            raise Exception(_("No parent tax code found in %s move") % move.name)
                    if move_line.tax_amount != 0.0:
                        tax_amount = (move_line.tax_amount * self.localcontext['data']['tax_sign'])
                    else:
                        tax_amount = move_line.tax_amount
                    if result.has_key(tax_code.id):
                        result[tax_code.id]['tax'] += tax_amount
                    else:
                        raise orm.except_orm(_("Tax codes malconfigured!"),
                            _("Tax code %s has not a base code!") % move_line.tax_code_id.name)
        return result

    def _get_tax_lines(self, move):
        res = []
        tax_code_obj = self.pool.get('account.tax.code')
        # index è usato per non ripetere la stampa dei dati fattura quando ci sono più codici IVA
        index = 0
        invoice = False
        for move_line in move.line_id:
            if move_line.invoice:
                if invoice and invoice.id != move_line.invoice.id:
                    raise Exception(_("Move %s contains different invoices") % move.name)
                invoice = move_line.invoice
        group_amounts_by_code = self._tax_amounts_by_code(move)
        #get total without withholding taxes
        amount_withholding = 0.0
        for line in invoice.tax_line:
            if line.tax_code_id.exclude_from_registries:
                amount_withholding += line.tax_amount
        if amount_withholding != 0.0:
            amount_total = invoice.amount_total - amount_withholding
        else:
            amount_total = invoice.amount_total

        for tax_code_id in group_amounts_by_code:
            tax_code = tax_code_obj.browse(self.cr, self.uid, tax_code_id)
            if group_amounts_by_code[tax_code_id]['base'] != 0:
                amount_total *= abs(group_amounts_by_code[tax_code_id]['base']) / group_amounts_by_code[tax_code_id]['base']
            tax_item = {
                'tax_code_name': tax_code.name,
                'amount': group_amounts_by_code[tax_code_id]['tax'],
                'base_amount': group_amounts_by_code[tax_code_id]['base'],
                'index': index,
                'invoice_date': (invoice and invoice.date_invoice
                                 or move.date or ''),
                'supplier_invoice_number': (invoice and invoice.supplier_invoice_number or ''),
                'amount_total': invoice and invoice.amount_total or '',
            }
            res.append(tax_item)
            index += 1
        return res

    def build_parent_tax_codes(self, tax_code):
        res = {}
        if tax_code.parent_id and tax_code.parent_id.parent_id:
            res[tax_code.parent_id.id] = True
            res.update(self.build_parent_tax_codes(tax_code.parent_id))
        return res
    
    def _compute_totals(self, tax_code_ids):
        res = []
        res_dict = {}
        tax_code_obj = self.pool.get('account.tax.code')
        for period_id in self.localcontext['data']['period_ids']:
            for tax_code in tax_code_obj.browse(
                    self.cr, self.uid, tax_code_ids, context={'period_id': period_id, }):
                if not res_dict.get(tax_code.id):
                    res_dict[tax_code.id] = 0.0
                res_dict[tax_code.id] += (tax_code.sum_period
                                          * self.localcontext['data']['tax_sign'])
        for tax_code_id in res_dict:
            tax_code = tax_code_obj.browse(self.cr, self.uid, tax_code_id)
            if res_dict[tax_code_id]:
                res.append((tax_code.name, res_dict[tax_code_id], tax_code.is_base))
        return res
    
    def _get_tax_codes(self):
        return self._compute_totals(self.localcontext['used_tax_codes'].keys())
        
    def _get_tax_codes_totals(self):
        parent_codes = {}
        tax_code_obj = self.pool.get('account.tax.code')
        for tax_code in tax_code_obj.browse(self.cr, self.uid,
                                            self.localcontext['used_tax_codes'].keys()):
            parent_codes.update(self.build_parent_tax_codes(tax_code))
        return self._compute_totals(parent_codes.keys())
        
    def _get_start_date(self):
        period_obj = self.pool.get('account.period')
        start_date = False
        for period in period_obj.browse(self.cr, self.uid,
                                        self.localcontext['data']['period_ids']):
            period_start = datetime.strptime(period.date_start, '%Y-%m-%d')
            if not start_date or start_date > period_start:
                start_date = period_start
        return start_date.strftime('%Y-%m-%d')
        
    def _get_end_date(self):
        period_obj = self.pool.get('account.period')
        end_date = False
        for period in period_obj.browse(self.cr, self.uid,
                                        self.localcontext['data']['period_ids']):
            period_end = datetime.strptime(period.date_stop, '%Y-%m-%d')
            if not end_date or end_date < period_end:
                end_date = period_end
        return end_date.strftime('%Y-%m-%d')

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'tax_lines': self._get_tax_lines,
            'tax_codes': self._get_tax_codes,
            'tax_codes_totals': self._get_tax_codes_totals,
            'used_tax_codes': {},
            'start_date': self._get_start_date,
            'end_date': self._get_end_date,
            'account_lines': self._get_account_lines,
        })

    def set_context(self, objects, data, ids, report_type=None):
        self.localcontext.update({
            'fiscal_page_base': data.get('fiscal_page_base'),
        })
        return super(Parser, self).set_context(objects, data, ids, report_type=report_type)

report_sxw.report_sxw('report.registro_iva_vendite',
                      'registro_iva_vendite',
                      'addons/l10n_it_vat_registries/templates/registro_iva_vendite.mako',
                      parser=Parser)
report_sxw.report_sxw('report.registro_iva_acquisti',
                      'registro_iva_acquisti',
                      'addons/l10n_it_vat_registries/templates/registro_iva_acquisti.mako',
                      parser=Parser)
report_sxw.report_sxw('report.registro_iva_corrispettivi',
                      'registro_iva_corrispettivi',
                      'addons/l10n_it_vat_registries/templates/registro_iva_corrispettivi.mako',
                      parser=Parser)
report_sxw.report_sxw('report.registro_generale',
                      'registro_generale',
                      'addons/l10n_it_vat_registries/templates/registro_generale.mako',
                      parser=Parser)
