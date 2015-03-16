# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>),
#    Copyright (C) 2012 Therp BV (<http://therp.nl>),
#    Copyright (C) 2013 Agile Business Group sagl
#    (<http://www.agilebg.com>) (<lorenzo.battistini@agilebg.com>)
#
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
from openerp.addons.account_financial_report_horizontal.report import (
    account_profit_loss
)
from common_report_header import common_report_header
from openerp.tools.translate import _


class report_balancesheet_horizontal(
    report_sxw.rml_parse, common_report_header
):

    def __init__(self, cr, uid, name, context=None):
        super(report_balancesheet_horizontal, self).__init__(
            cr, uid, name, context=context)
        self.obj_pl = account_profit_loss.report_pl_account_horizontal(
            cr, uid, name, context=context)
        self.result_sum_dr = 0.0
        self.result_sum_cr = 0.0
        self.result = {}
        self.res_bl = {}
        self.result_temp = []
        self.localcontext.update({
            'time': time,
            'get_lines': self.get_lines,
            'get_lines_another': self.get_lines_another,
            'sum_dr': self.sum_dr,
            'sum_cr': self.sum_cr,
            'sum_partial_dr': self.sum_partial_dr,
            'sum_partial_cr': self.sum_partial_cr,
            'get_data': self.get_data,
            'get_pl_balance': self.get_pl_balance,
            'get_fiscalyear': self._get_fiscalyear,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_sortby': self._get_sortby,
            'get_filter': self._get_filter,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_target_move': self._get_target_move,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] \
                and data['form']['chart_account_id'] \
                and [data['form']['chart_account_id'][0]] or []
            objects = self.pool.get('account.account').browse(
                self.cr, self.uid, new_ids)
            lang_dict = self.pool.get('res.users').read(
                self.cr, self.uid, self.uid, ['context_lang'])
            data['lang'] = lang_dict.get('context_lang') or False
        return super(
            report_balancesheet_horizontal, self
        ).set_context(objects, data, new_ids, report_type=report_type)

    def sum_partial_dr(self):
        return self.result_sum_dr

    def sum_partial_cr(self):
        return self.result_sum_cr

    def sum_dr(self):
        if self.res_bl['type'] == _('Net Profit'):
            self.result_sum_dr += self.res_bl['balance']
        return self.result_sum_dr

    def sum_cr(self):
        if self.res_bl['type'] == _('Net Loss'):
            self.result_sum_cr += self.res_bl['balance']
        return self.result_sum_cr

    def get_pl_balance(self):
        return self.res_bl

    def get_data(self, data):
        cr, uid = self.cr, self.uid

        # Getting Profit or Loss Balance from profit and Loss report
        self.obj_pl.get_data(data)
        self.res_bl = self.obj_pl.final_result()

        account_pool = self.pool['account.account']
        currency_pool = self.pool['res.currency']

        types = [
            'liability',
            'asset'
        ]

        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form'].get('fiscalyear_id', False)
        if ctx['fiscalyear']:
            ctx['fiscalyear'] = ctx['fiscalyear'][0]

        if data['form']['filter'] == 'filter_period':
            ctx['periods'] = data['form'].get('periods', False)
        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form'].get('date_from', False)
            ctx['date_to'] = data['form'].get('date_to', False)
        ctx['state'] = data['form'].get('target_move', 'all')
        cal_list = {}
        account_dict = {}
        account_id = data['form'].get('chart_account_id', False)
        if account_id:
            account_id = account_id[0]
        chart = self.pool['account.chart.template'].browse(cr, 1, account_id)
        account_ids = account_pool._get_children_and_consol(
            cr, uid, account_id, context=ctx)
        accounts = account_pool.browse(cr, uid, account_ids, context=ctx)

        if not self.res_bl:
            self.res_bl['type'] = _('Net Profit')
            self.res_bl['balance'] = 0.0

        if self.res_bl['type'] == _('Net Profit'):
            self.res_bl['type'] = _('Net Profit')
        else:
            self.res_bl['type'] = _('Net Loss')
        pl_dict = {
            'code': self.res_bl['type'],
            'name': self.res_bl['type'],
            'level': False,
            'balance': self.res_bl['balance'],
            'type': self.res_bl['type'],
        }
        accounts_temp = []
        accounts_l_temp = []
        accounts_a_temp = []
        for typ in types:
            
            for account in accounts:
                if (account.user_type.report_type) and (account.user_type.report_type == typ) and (
                    account.parent_id.code != chart.property_account_receivable.code) and (
                    account.parent_id.code != chart.property_account_payable.code):
                    account_dict = {
                        'id': account.id,
                        'code': account.code,
                        'name': account.name,
                        'level': account.level,
                        'balance': (
                            account.balance and typ == 'liability' and -1 or 1
                        ) * account.balance,
                        'type': account.type,
                    }
                    currency = (account.currency_id and account.currency_id or account.company_id.currency_id)
#                     if typ == 'liability' and account.type != 'view' and (account.debit != account.credit):
#                         self.result_sum_dr += account_dict['balance']
#                     if typ == 'asset' and account.type != 'view' and (account.debit != account.credit):
#                         self.result_sum_cr += account_dict['balance']

#sum negative asset as positive in liability and viceversa
                    if (typ == 'liability' and account_dict['balance'] >= 0.0 or
                        typ == 'asset' and account_dict['balance'] < 0.0
                        ) and account.type != 'view' and (account.debit != account.credit):
                            self.result_sum_dr += (typ == 'liability' and 1 or -1) * account_dict['balance']
                    if (typ == 'asset' and account_dict['balance'] >= 0.0 or
                        typ == 'liability' and account_dict['balance'] < 0.0
                        ) and account.type != 'view' and (account.debit != account.credit):
                        self.result_sum_cr += (typ == 'asset' and 1 or -1) * account_dict['balance']

#                     #put in asset negative liability and change sign to positive, and viceversa for liability
#                     if account_dict['type'] == 'asset' and account_dict['balance'] < 0.0:
#                         account_dict.update({'type': 'liability', 'balance': account_dict['balance'] * -1})
#                     if account_dict['type'] == 'liability' and account_dict['balance'] < 0.0:
#                         account_dict.update({'type': 'asset', 'balance': account_dict['balance'] * -1})

                    if data['form']['display_account'] == 'bal_movement':
                        if (
                            not currency_pool.is_zero(
                                self.cr, self.uid, currency, account.credit
                            )) or (
                                not currency_pool.is_zero(
                                    self.cr, self.uid, currency, account.debit
                                )
                        ) or (
                                not currency_pool.is_zero(
                                    self.cr, self.uid, currency,
                                    account.balance
                                )
                        ):
                            if typ == 'liability' and account_dict['balance'] >= 0.0:
                                accounts_l_temp.append(account_dict)
                            if typ == 'asset' and account_dict['balance'] < 0.0:
                                account_dict.update({'balance': account_dict['balance'] * -1})
                                accounts_l_temp.append(account_dict)
                            if typ == 'asset' and account_dict['balance'] >= 0.0:
                                accounts_a_temp.append(account_dict)
                            if typ == 'liability' and account_dict['balance'] < 0.0:
                                account_dict.update({'balance': account_dict['balance'] * -1})
                                accounts_a_temp.append(account_dict)
                    elif data['form']['display_account'] == 'bal_solde':
                        if not currency_pool.is_zero(
                            self.cr, self.uid, currency, account.balance
                            ):
                            #append positive liability or negative asset in liability column
                            if typ == 'liability' and account_dict['balance'] >= 0.0:
                                accounts_l_temp.append(account_dict)
                            if typ == 'asset' and account_dict['balance'] < 0.0:
                                account_dict.update({'balance': account_dict['balance'] * -1})
                                accounts_l_temp.append(account_dict)
                            if typ == 'asset' and account_dict['balance'] >= 0.0:
                                accounts_a_temp.append(account_dict)
                            if typ == 'liability' and account_dict['balance'] < 0.0:
                                account_dict.update({'balance': account_dict['balance'] * -1})
                                accounts_a_temp.append(account_dict)
                    else:
                        if typ == 'liability' and account_dict['balance'] >= 0.0:
                            accounts_l_temp.append(account_dict)
                        if typ == 'asset' and account_dict['balance'] < 0.0:
                            account_dict.update({'balance': account_dict['balance'] * -1})
                            accounts_l_temp.append(account_dict)
                        if typ == 'asset' and account_dict['balance'] >= 0.0:
                            accounts_a_temp.append(account_dict)
                        if typ == 'liability' and account_dict['balance'] < 0.0:
                            account_dict.update({'balance': account_dict['balance'] * -1})
                            accounts_a_temp.append(account_dict)

            
            #add supplier and customer total
            if typ == 'liability':
                account_view_id = account_pool.search(cr, uid, [('code', '=', chart.property_account_payable.code)])
            if typ == 'asset':
                account_view_id = account_pool.search(cr, uid, [('code', '=', chart.property_account_receivable.code)])
            account_view = account_pool.browse(cr, uid, account_view_id[0])
            account_dict = {
                    'id': account_view.id,
                    'code': account_view.code,
                    'name': account_view.name,
                    'level': account_view.level,
                    'balance': (
                        account_view.balance and typ == 'liability' and -1 or 1
                    ) * account_view.balance,
                    'type': account_view.type,
                }
            if typ == 'liability':
                self.result_sum_dr += account_dict['balance']
                accounts_l_temp.append(account_dict)
            if typ == 'asset':
                self.result_sum_cr += account_dict['balance']
                accounts_a_temp.append(account_dict)

        cal_list['asset'] = self.result['asset'] = accounts_a_temp
        cal_list['liability'] = self.result['liability'] = accounts_l_temp

        if pl_dict['code'] == _('Net Loss'):
            self.result['asset'].append(pl_dict)
        else:
            self.result['liability'].append(pl_dict)

        if cal_list:
            temp = {}
            for i in range(
                0, max(len(cal_list['liability']), len(cal_list['asset']))
            ):
                if i < len(cal_list['liability']) and i < len(
                    cal_list['asset']
                ):
                    temp = {
                        'code': cal_list['liability'][i]['code'],
                        'name': cal_list['liability'][i]['name'],
                        'level': cal_list['liability'][i]['level'],
                        'balance': cal_list['liability'][i]['balance'],
                        'type': cal_list['liability'][i]['type'],
                        'code1': cal_list['asset'][i]['code'],
                        'name1': cal_list['asset'][i]['name'],
                        'level1': cal_list['asset'][i]['level'],
                        'balance1': cal_list['asset'][i]['balance'],
                        'type1': cal_list['asset'][i]['type'],
                    }
                    self.result_temp.append(temp)
                else:
                    if i < len(cal_list['asset']):
                        temp = {
                            'code': '',
                            'name': '',
                            'level': False,
                            'balance': False,
                            'type': False,
                            'code1': cal_list['asset'][i]['code'],
                            'name1': cal_list['asset'][i]['name'],
                            'level1': cal_list['asset'][i]['level'],
                            'balance1': cal_list['asset'][i]['balance'],
                            'type1': cal_list['asset'][i]['type'],
                        }
                        self.result_temp.append(temp)
                    if i < len(cal_list['liability']):
                        temp = {
                            'code': cal_list['liability'][i]['code'],
                            'name': cal_list['liability'][i]['name'],
                            'level': cal_list['liability'][i]['level'],
                            'balance': cal_list['liability'][i]['balance'],
                            'type': cal_list['liability'][i]['type'],
                            'code1': '',
                            'name1': '',
                            'level1': False,
                            'balance1': False,
                            'type1': False,
                        }
                        self.result_temp.append(temp)
        return None

    def get_lines(self):
        return self.result_temp

    def get_lines_another(self, group):
        return self.result.get(group, [])

report_sxw.report_sxw(
    'report.account.balancesheet.horizontal', 'account.account',
    'addons/account_financial_report_horizontal/report/'
    'account_balance_sheet_horizontal.rml',
    parser=report_balancesheet_horizontal,
    header='internal landscape')

report_sxw.report_sxw(
    'report.account.balancesheet', 'account.account',
    'addons/account_financial_report_horizontal/report/'
    'account_balance_sheet.rml',
    parser=report_balancesheet_horizontal,
    header='internal')
