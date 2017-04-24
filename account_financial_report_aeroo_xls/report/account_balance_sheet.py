# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) BrowseInfo (http://browseinfo.in)
#    Copyright (C) Didotech SRL
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

import time

from openerp.report import report_sxw
from common_report_header import common_report_header
from openerp.tools.translate import _


class Parser(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_lines': self.get_lines,
            'time': time,
            'get_fiscalyear': self._get_fiscalyear,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_filter': self._get_filter,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'compute_currency': self.compute_currency,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if data['model'] == 'ir.ui.menu':
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id'][0]] or []
            objects = self.pool['account.account'].browse(self.cr, self.uid, new_ids, self.context)
        return super(Parser, self).set_context(objects, data, new_ids, report_type=report_type)

    def get_lines(self, data):
        lines = []
        account_obj = self.pool['account.account']
        currency_obj = self.pool['res.currency']
        context_account = data['form']['used_context']
        ids2 = self.pool['account.financial.report']._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id'][0]], context=data['form']['used_context'])

        for report in self.pool['account.financial.report'].browse(self.cr, self.uid, ids2, context=context_account):
            vals = {
                'name': report.name,
                'balance': report.balance,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type == 'sum' and 'view' or False,  # used to underline the financial report balances
            }
            # if data['form']['debit_credit']:
            #     vals['debit'] = report.debit
            #     vals['credit'] = report.credit
            # if data['form']['enable_filter']:
            #     vals['balance_cmp'] = self.pool['account.financial.report'].browse(self.cr, self.uid, report.id, context=data['form']['comparison_context']).balance
            lines.append(vals)
            account_ids = []
            if report.display_detail == 'no_detail':
                # the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue
            if report.type == 'accounts' and report.account_ids:
                account_ids = account_obj._get_children_and_consol(self.cr, self.uid, [x.id for x in report.account_ids], self.context)
            elif report.type == 'account_type' and report.account_type_ids:
                account_ids = account_obj.search(self.cr, self.uid, [('user_type', 'in', [x.id for x in report.account_type_ids])], context=self.context)
            sum_dr = 0
            sum_cr = 0
            if account_ids:
                for account in account_obj.browse(self.cr, self.uid, account_ids, context=context_account):
                    # if there are accounts to display, we add them to the lines with a level equals to their level in
                    # the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    # financial reports for Assets, liabilities...)
                    if report.display_detail == 'detail_flat' and account.type == 'view':
                        continue
                    flag = False
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'account_name': account.name,
                        'balance':  account.balance != 0 and account.balance or account.balance,
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and min(account.level, 6) or 6,  # account.level + 1
                        'account_view_type': account.type,
                        'code': account.code,
                        'account_type': account.user_type.report_type
                    }

                    # if data['form']['debit_credit']:
                    #     vals['debit'] = account.debit
                    #     vals['credit'] = account.credit

                    if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance']):
                        flag = True
                        if account.type != 'view':
                            if account.user_type.report_type in ['expense', 'liability']:
                                sum_dr += account.balance
                            if account.user_type.report_type in ['income', 'asset']:
                                sum_cr += account.balance
                    # if data['form']['enable_filter']:
                    #     vals['balance_cmp'] = account_obj.browse(self.cr, self.uid, account.id, context=data['form']['comparison_context']).balance
                    #     if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance_cmp']):
                    #         flag = True
                    if flag:
                        lines.append(vals)

                if sum_dr:
                    vals = {
                        'name': _('Total'),
                        'account_name': '',
                        'balance': sum_dr,
                        'code': _('Total'),
                        'account_type': 'expense',
                        'account_view_type': 'view',
                    }
                    lines.append(vals)
                if sum_cr:
                    vals = {
                        'name': _('Total'),
                        'account_name': '',
                        'balance': sum_cr,
                        'code': _('Total'),
                        'account_type': 'income',
                        'account_view_type': 'view',
                    }
                    lines.append(vals)

                print sum_dr, sum_cr

        return lines

    def compute_currency(self, to_currency, from_currency, amt):
        currency_obj = self.pool['res.currency']
        curr_current = from_currency
        if to_currency:
            curr_current = to_currency[0]
        amount = currency_obj.compute(self.cr, self.uid, curr_current, from_currency, amt)
        return '{amount}'.format(amount=abs(amount)).replace('.', ',')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
