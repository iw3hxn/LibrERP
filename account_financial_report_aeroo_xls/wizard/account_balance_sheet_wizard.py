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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class account_balance_sheet_report(orm.TransientModel):
    """
    This wizard will provide the account balance sheet report by periods, between any two dates.
    """
    _inherit = 'account.bs.report'
    _columns = {
        'currency_id': fields.many2one('res.currency', 'Currency'),
    }

    def _print_report_excel(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_balance_sheet_excel',
            'datas': data
        }

    def check_report_excel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data = {
            'ids': context.get('active_ids', []),
            'model': context.get('active_model', 'ir.ui.menu'),
            'form': self.read(cr, uid, ids, [
                'date_from', 'date_to', 'fiscalyear_id', 'period_from', 'display_account',
                'period_to', 'filter', 'chart_account_id', 'target_move', 'currency_id'
            ])[0],
        }

        data['form']['lang'] = self.pool['res.users'].browse(cr, uid, uid, context).context_lang
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = used_context

        report_model, report_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'account',
                                                                                  'account_financial_report_balancesheet0')
        report_name = self.pool[report_model].browse(cr, uid, report_id, context).name
        data['form']['account_report_id'] = (report_id, report_name)

        for field in ['fiscalyear', 'chart_account_id', 'period_from', 'period_to']:
            if data['form']['used_context'].get(field, False) and isinstance(data['form']['used_context'][field],
                                                                             tuple):
                data['form']['used_context'][field] = data['form']['used_context'][field][0]

        return self._print_report_excel(cr, uid, ids, data, context=context)


class account_profit_loss_report(orm.TransientModel):
    """
    This wizard will provide the account balance sheet report by periods, between any two dates.
    """
    _inherit = 'account.pl.report'
    _columns = {
        'currency_id': fields.many2one('res.currency', 'Currency'),
    }

    def _print_report_excel(self, cr, uid, ids, data, context=None):

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_profit_loss_excel',
            'datas': data
        }

    def check_report_excel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data = {
            'ids': context.get('active_ids', []),
            'model': context.get('active_model', 'ir.ui.menu'),
            'form': self.read(cr, uid, ids, [
                'date_from', 'date_to', 'fiscalyear_id', 'period_from', 'display_account',
                'period_to', 'filter', 'chart_account_id', 'target_move', 'currency_id'
            ])[0],
        }

        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = used_context

        report_model, report_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'account',
                                                                                  'account_financial_report_profitandloss0')
        report_name = self.pool[report_model].browse(cr, uid, report_id, context).name
        data['form']['account_report_id'] = (report_id, report_name)

        for field in ['fiscalyear', 'chart_account_id', 'period_from', 'period_to']:
            if data['form']['used_context'].get(field, False) and isinstance(data['form']['used_context'][field], tuple):
                data['form']['used_context'][field] = data['form']['used_context'][field][0]

        return self._print_report_excel(cr, uid, ids, data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
