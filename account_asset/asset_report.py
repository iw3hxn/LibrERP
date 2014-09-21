# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2014 Didotech srl (www.didotech.com).
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
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)


class Parser(report_sxw.rml_parse):

    def _get_invoiced_account_move_lines(self, asset):
        res = []
        invoice = False
        for move_line in asset.account_move_line_ids:
            if move_line.asset_category_id:
                if move_line.invoice:
                    #if invoice and invoice.id != move_line.invoice.id:
                    #    raise Exception(_("Move %s contains different invoices") % asset.name)
                    invoice = move_line.invoice
                account_item = {
                    'amount': move_line.tax_amount,
                    'account_name': move_line.account_id.name,
                    'partner_name': move_line.invoice.partner_id.name,
                    'ref': move_line.ref,
                    'invoice_date': (invoice and invoice.date_invoice or ''),
                    'supplier_invoice_number': (invoice and invoice.supplier_invoice_number or ''),
                }
                res.append(account_item)
        return res

    def _get_asset_fy_depreciation_sum(self, asset):
        asset_fy_depreciation_amount = 0.0
        fy = self.pool['account.fiscalyear'].browse(self.cr, self.uid, self.localcontext['fy_id'])[0]
        for asset_dl in asset.depreciation_line_ids:
            if asset_dl.line_date <= fy.date_stop and asset_dl.line_date >= fy.date_start and asset_dl.type == 'depreciate':
                asset_fy_depreciation_amount += asset_dl.amount
        return asset_fy_depreciation_amount

    def _get_asset_start_year(self, asset):
        res = False
        if asset.date_start:
            date_start = datetime.strptime(asset.date_start, DEFAULT_SERVER_DATE_FORMAT)
            res = str(date_start.year)
        return res

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'invoiced_asset_lines': self._get_invoiced_account_move_lines,
            'asset_start_year': self._get_asset_start_year,
            'asset_fy_depreciation_amount': self._get_asset_fy_depreciation_sum,
        })

    def set_context(self, objects, data, ids, report_type=None):
        self.localcontext.update({
            'fiscal_page_base': data.get('fiscal_page_base'),
            'start_date': data.get('date_start'),
            'fy_name': data.get('fy_name'),
            'type': data.get('type'),
            'fy_id': data.get('fy_id'),
        })
        return super(Parser, self).set_context(objects, data, ids, report_type=report_type)

report_sxw.report_sxw('report.asset_report',
                      'asset_report',
                      'addons/account_asset/templates/asset_report.mako',
                      parser=Parser)
