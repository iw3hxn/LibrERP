# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016-2017 Didotech srl (http://www.didotech.com)
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from datetime import date, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from xlwt import Workbook, easyxf, Formula
from cStringIO import StringIO
import collections
import string


class ColumnName(dict):
    """
        Numeration starts from 0
        0 - A
        1 - B
        etc
    """
    def __init__(self):
        super(ColumnName, self).__init__()
        self.alphabet = string.uppercase
        self.alphabet_size = len(self.alphabet)

    def __missing__(self, column_number):
        ret = self[column_number] = self.get_column_name(column_number)
        return ret

    def get_column_name(self, column_number):
        # print column_number
        column_number += 1

        if column_number <= self.alphabet_size:
            return self.alphabet[column_number - 1]
        else:
            return self.alphabet[((column_number - 1) / self.alphabet_size) - 1] + self.alphabet[
                ((column_number - 1) % self.alphabet_size)]


COLUMN_NAMES = ColumnName()


class Style:
    bold_header = easyxf('font: bold on; align: horiz center;')
    title = easyxf('font: bold on; borders: left thin, top thin, right thin; align: horiz center;')


class ExportSalesTeamReport(orm.TransientModel):
    _name = 'export.sales.team.report'

    _description = "Export revenue on month basis for selected Sales Team"

    def get_years_selection(self, cr, uid, context):
        cr.execute("""SELECT EXTRACT(YEAR FROM date_order) as year
            FROM sale_order
            GROUP BY year
            ORDER BY year
        """)
        sale_orders = cr.fetchall()
        years_order = [(str(int(year[0])), str(int(year[0]))) for year in sale_orders if year[0]]

        cr.execute("""SELECT EXTRACT(YEAR FROM date_invoice) as year
                    FROM account_invoice
                    GROUP BY year
                    ORDER BY year
                """)
        invoices = cr.fetchall()
        years_invoice = [(str(int(year[0])), str(int(year[0]))) for year in invoices if year[0]]
        return list(set(years_order).union(years_invoice))

    _columns = {
        'data': fields.binary("File", readonly=True),
        'name': fields.char('Filename', 64, readonly=True),
        'year': fields.selection(get_years_selection, _('Year'), required=True),
        'state': fields.selection(
            (
                ('selection', 'selection'),
                ('end', 'end')
            ), 'state', required=True, translate=False, readonly=True
        ),
        'model': fields.selection(
            (
                ('sale.order', _('Sale')),
                ('account.invoice', _('Invoice')),
                ('account.move.line', _('Paid')),
                ('invoice.paid', _('Invoice/Paid'))
            ), _('Base model'), required=True
        )
    }

    _defaults = {
        'state': lambda *a: 'selection',
    }

    table_layout = collections.OrderedDict({
        0: {'name': 'CLIENTE', 'width': 10000},
        1: {'name': 'year', 'width': 2000},
        2: {'name': 'totale', 'width': 3000}
    })

    @staticmethod
    def get_query(date_start, date_end, section_id, model='sale.order', account_ids=''):
        if model == 'sale.order':
            return """SELECT partner_id, SUM(amount_untaxed)
                    FROM sale_order
                    WHERE date_order >= '{date_start}'
                    AND date_order <= '{date_end}'
                    AND state IN ('manual', 'progress', 'done')
                    AND section_id = {section_id}
                    GROUP BY partner_id""".format(date_start=date_start.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                                  date_end=date_end.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                                  section_id=section_id)
        elif model == 'account.invoice':
            return """SELECT partner_id,
                    SUM(CASE WHEN type='out_invoice' THEN amount_untaxed
                        WHEN type='out_refund' THEN -1 * amount_untaxed
                    END) AS amount_total
                    FROM account_invoice
                    WHERE date_invoice >= '{date_start}'
                    AND date_invoice <= '{date_end}'
                    AND state NOT IN ('draft', 'proforma')
                    AND type in ('out_invoice', 'out_refund')
                    AND section_id = {section_id}
                    GROUP BY partner_id""".format(date_start=date_start.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                                  date_end=date_end.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                                  section_id=section_id)
        elif model == 'account.move.line':
            return """SELECT rp.id AS partner_id, (SUM(aml.credit) - SUM(aml.debit)) AS amount_total
                        FROM account_move_line AS aml
                        JOIN res_partner AS rp
                          ON aml.partner_id = rp.id
                        JOIN account_journal AS aj
                          ON aml.journal_id = aj.id
                       WHERE aml.date >= '{date_start}'
                         AND aml.date <= '{date_end}'
                         AND aml.state = 'valid'
                         AND aml.account_id IN ({account_ids})
                         AND aj.type IN ('cash', 'bank')
                         AND rp.section_id = {section_id}
                    GROUP BY rp.id;
            """.format(date_start=date_start.strftime(DEFAULT_SERVER_DATE_FORMAT),
                       date_end=date_end.strftime(DEFAULT_SERVER_DATE_FORMAT),
                       account_ids=account_ids,
                       section_id=section_id)

    @staticmethod
    def get_period(year, month):
        start_date = date(year, month, 1)
        end_date = start_date + relativedelta(months=1) - relativedelta(days=1)
        return start_date, end_date

    @staticmethod
    def write_header_info(ws, currency):
        now = datetime.now()
        ws.write(1, 0, 'DATA: {}'.format(now.strftime('%d/%m/%Y')))
        ws.write(1, 2, 'ORA: {}'.format(now.strftime('%H:%M')))
        ws.write(2, 0, 'Divisa: {}'.format(currency.name))

    def write_header(self, ws, row):
        for column, layout in self.table_layout.items():
            ws.write(row, column, layout['name'], Style.bold_header)
            ws.col(column).width = layout['width']

        for month in range(1, 13):
            ws.write(row, month + column, date(2000, month, 1).strftime('%B'), Style.bold_header)

        return ws

    def write_header_invoice_paid(self, ws, row):
        for column, layout in self.table_layout.items():
            if layout['name'] == 'totale':
                ws.write_merge(r1=4, c1=2, r2=4, c2=6, label=layout['name'], style=Style.title)

            else:
                ws.write(row, column, layout['name'], Style.bold_header)
                ws.col(column).width = layout['width']

        col = 7

        for month in range(1, 13):
            ws.write_merge(r1=4, c1=col, r2=4, c2=col + 4, label=date(2000, month, 1).strftime('%B'), style=Style.title)
            col += 5

        # for month in range(1, 13):
        #     if col % 2 == 0:
        #         ws.write(row, col, date(2000, month, 1).strftime('%B'), Style.bold_header)
        #         ws.write(row, col + 1, '', Style.bold_header)
        #         col += 2

        col = 2
        row += 1

        for month in range(1, 14):
            ws.write(row, col, 'Fatt', Style.bold_header)
            ws.write(row, col + 1, 'Incass', Style.bold_header)
            ws.write(row, col + 2, 'Provv. su ft', Style.bold_header)
            ws.write(row, col + 3, 'Provv. su inc.', Style.bold_header)
            ws.write(row, col + 4, 'Provv. resid', Style.bold_header)
            col += 5

        return ws, row

    @staticmethod
    def write_table(ws, row, values, year):
        ws.write(row, 0, values['name'])
        ws.write(row, 1, year)
        ws.write(row, 2, values['total_amount'], Style.currency)

        for month in range(1, 13):
            ws.write(row, month + 2, values.get(month, 0), Style.currency)

    @staticmethod
    def write_total(ws, row, first_row):
        row += 1
        last_row = row

        last_column = 1 + 13 * 1

        for column in range(2, last_column + 1):
            ws.write(row, column,
                     Formula("SUM({column}{start}:{column}{end})".format(column=COLUMN_NAMES[column],
                                                                         start=first_row + 1,
                                                                         end=last_row)),
                     Style.currency_bold)

    @staticmethod
    def write_total_invoice_paid(ws, row, first_row):
        row += 1
        last_row = row
        column = 2

        last_column = 1 + 13 * 5

        for i in range(1, last_column):
            if column % 2 == 0:
                border_currency = Style.last_col_currency_border_left
            else:
                border_currency = Style.currency_bold

            if i == last_column:
                border_currency = Style.last_col_currency_border_bold

            ws.write(row, column,
                     Formula("SUM({column}{start}:{column}{end})".format(column=COLUMN_NAMES[column],
                                                                         start=first_row + 1,
                                                                         end=last_row)),
                     border_currency)
            column += 1

    @staticmethod
    def write_table_invoice_paid(ws, row, values, year, commission):
        if 'total_amount_invoice' in values:
            if 'total_amount_paid' in values:
                value_i = values['total_amount_invoice']
                value_p = values['total_amount_paid']
            else:
                value_i = values['total_amount_invoice']
                value_p = 0
        else:
            value_i = 0
            value_p = values['total_amount_paid']

        ws.write(row, 0, values['name'])
        ws.write(row, 1, year)
        ws.write(row, 2, value_i, Style.currency_border_left)
        col = 2
        ws.write(row, 3, value_p, Style.currency)
        ws.write(
            row, 4,
            Formula("{column}{row}*{commission}".format(
                column=COLUMN_NAMES[col], row=row + 1, commission=commission)
            ),
            Style.currency_border_left
        )

        ws.write(
            row, 5,
            Formula("{column}{row}*{commission}".format(
                column=COLUMN_NAMES[col + 1], row=row + 1, commission=commission)
            ),
            Style.currency
        )
        col = 2
        ws.write(
            row, 6,
            Formula("{invoiced_column}{row}-{column}{row}".format(
                invoiced_column=COLUMN_NAMES[col + 2], column=COLUMN_NAMES[col + 3], row=row + 1)
            ),
            Style.currency
        )

        col = 7
        style_currency = Style.currency

        for month in range(1, 13):
            if month == 12:
                style_currency = Style.last_col_currency_border

            month_i = str(month) + 'i'
            month_p = str(month) + 'p'
            ws.write(row, col, values.get(month_i, 0), Style.currency_border_left)
            ws.write(row, col + 1, values.get(month_p, 0), style_currency)
            ws.write(
                row, col + 2,
                Formula("{column}{row}*{commission}".format(
                    column=COLUMN_NAMES[col], row=row + 1, commission=commission)
                ),
                Style.currency
            )
            ws.write(
                row, col + 3,
                Formula("{column}{row}*{commission}".format(
                    column=COLUMN_NAMES[col + 1], row=row + 1, commission=commission)
                ),
                Style.currency
            )
            ws.write(
                row, col + 4,
                Formula("{invoiced_column}{row}-{column}{row}".format(
                    invoiced_column=COLUMN_NAMES[col + 2], column=COLUMN_NAMES[col + 3], row=row + 1)
                ),
                Style.currency
            )

            col += 5

    def action_team_report(self, cr, uid, ids, context):
        wizard = self.browse(cr, uid, ids[0], context)
        year = int(wizard.year)
        currency = self.pool['res.users'].browse(cr, uid, uid, context).company_id.currency_id
        partner_obj = self.pool['res.partner']

        file_name = 'Sales_Team_{model}_{year}.xls'.format(model=wizard.model, year=year)

        book = Workbook(encoding='utf-8')

        for section in self.pool['crm.case.section'].browse(cr, uid, context['active_ids'], context):
            # ws = book.add_sheet(name, cell_overwrite_ok=True)
            ws = book.add_sheet(section.name)

            if wizard.model == 'invoice.paid':
                query = self.get_query(date(year, 1, 1), date(year, 12, 31), section.id, 'account.invoice')
                cr.execute(query)
                results = cr.fetchall()
                results = dict(results)

                partner_ids = partner_obj.search(cr, uid, [('section_id', '=', section.id)], context=context)
                account_ids = []
                for partner in partner_obj.browse(cr, uid, partner_ids, context=context):
                    if partner.property_account_receivable:
                        if not str(partner.property_account_receivable.id) in account_ids:
                            account_ids.append(str(partner.property_account_receivable.id))
                account_ids = ','.join(account_ids)

                if account_ids:
                    query = self.get_query(date(year, 1, 1), date(year, 12, 31), section.id, 'account.move.line', account_ids)
                    cr.execute(query)
                    results2 = cr.fetchall()
                    results2 = dict(results2)
                else:
                    results2 = {}

                report = {}
                for partner in self.pool['res.partner'].browse(cr, uid, results.keys(), context=context):
                    report[partner.id] = {
                        'name': partner.name,
                        'total_amount_invoice': results[partner.id]
                    }

                for partner in self.pool['res.partner'].browse(cr, uid, results2.keys(), context=context):
                    if partner.id in report:
                        report[partner.id].update({'total_amount_paid': results2[partner.id]})
                    else:
                        report[partner.id] = {
                            'name': partner.name,
                            'total_amount_paid': results2[partner.id]
                        }

                for month in range(1, 13):
                    date_start, date_end = self.get_period(year, month)
                    query = self.get_query(date_start, date_end, section.id, 'account.invoice')
                    cr.execute(query)
                    results = cr.fetchall()

                    if account_ids:
                        query = self.get_query(date_start, date_end, section.id, 'account.move.line', account_ids)
                        cr.execute(query)
                        results2 = cr.fetchall()
                    else:
                        results2 = {}

                    month_i = str(month) + 'i'
                    month_p = str(month) + 'p'

                    for key, value in results:
                        report[key].update({month_i: value})

                    for key, value in results2:
                        report[key].update({month_p: value})

                ws.write(0, 5, 'Fatturato/Incassato Mensile Clienti', Style.bold_header)

                self.write_header_info(ws, currency)

                Style.currency = easyxf('align: horiz right;',
                                        num_format_str=u'{symbol}#,##0.00'.format(symbol=currency.symbol))
                Style.currency_bold = easyxf('font: bold on; align: horiz right',
                                             num_format_str=u'{symbol}#,##0.00'.format(symbol=currency.symbol))
                Style.currency_border_left = easyxf('align: horiz right; borders: left thin;',
                                                    num_format_str=u'{symbol}#,##0.00'.format(symbol=currency.symbol))
                Style.last_col_currency_border_left = easyxf('align: horiz right; borders: left thin; font: bold on;',
                                                    num_format_str=u'{symbol}#,##0.00'.format(symbol=currency.symbol))
                Style.last_col_currency_border = easyxf('align: horiz right; borders: right thin;',
                                                        num_format_str=u'{symbol}#,##0.00'.format(symbol=currency.symbol))
                Style.last_col_currency_border_bold = easyxf('align: horiz right; borders: right thin; font: bold on;',
                                                             num_format_str=u'{symbol}#,##0.00'.format(symbol=currency.symbol))

                row = 4

                ws, row = self.write_header_invoice_paid(ws, row)

                first_row = row + 1

                if report:
                    for row, item in enumerate(report.items(), first_row):
                        partner_id, values = item
                        if section.sale_agent_id and section.sale_agent_id.commission:
                            commission_value = section.sale_agent_id.commission.get_commission(partner_id) * 0.01
                        else:
                            commission_value = 0.0
                        self.write_table_invoice_paid(ws, row, values, year, commission_value)
                else:
                    row = first_row
                    values = {'name': '', 'total_amount_invoice': 0, 'total_amount_paid': 0}
                    if section.sale_agent_id and section.sale_agent_id.commission:
                        commission_value = section.sale_agent_id.commission.get_commission() * 0.01
                    else:
                        commission_value = 0.0
                    self.write_table_invoice_paid(ws, row, values, year, commission_value)

                self.write_total_invoice_paid(ws, row, first_row)
            else:
                query = self.get_query(date(year, 1, 1), date(year, 12, 31), section.id, wizard.model)
                cr.execute(query)
                results = cr.fetchall()
                results = dict(results)

                report = {}

                for partner in self.pool['res.partner'].browse(cr, uid, results.keys(), context=context):
                    report[partner.id] = {
                        'name': partner.name,
                        'total_amount': results[partner.id]
                    }

                for month in range(1, 13):
                    date_start, date_end = self.get_period(year, month)
                    query = self.get_query(date_start, date_end, section.id, wizard.model)
                    cr.execute(query)
                    results = cr.fetchall()

                    for key, value in results:
                        report[key].update({month: value})

                if wizard.model == 'sale.order':
                    ws.write(0, 5, 'Ordinato Mensile Clienti', Style.bold_header)
                elif wizard.model == 'account.invoice':
                    ws.write(0, 5, 'Fatturato Mensile Clienti', Style.bold_header)
                elif wizard.model == 'account.move.line':
                    ws.write(0, 5, 'Incassato Mensile Clienti', Style.bold_header)
                else:
                    ws.write(0, 5, 'Fatturato/Incassato Mensile Clienti', Style.bold_header)

                self.write_header_info(ws, currency)

                Style.currency = easyxf('align: horiz right', num_format_str=u'{symbol}#,##0.00'.format(symbol=currency.symbol))
                Style.currency_bold = easyxf('font: bold on; align: horiz right', num_format_str=u'{symbol}#,##0.00'.format(symbol=currency.symbol))

                ws = self.write_header(ws, 4)
                first_row = 5

                if report:
                    for row, item in enumerate(report.items(), first_row):
                        partner_id, values = item
                        self.write_table(ws, row, values, year)

                    self.write_total(ws, row, first_row)
                else:
                    row = first_row
                    values = {'name': '', 'total_amount': 0}
                    self.write_table(ws, row, values, year)
                    self.write_total(ws, row, first_row)

        """PARSING DATA AS STRING """
        file_data = StringIO()
        book.save(file_data)
        """STRING ENCODE OF DATA IN WKSHEET"""
        out = file_data.getvalue()
        out = out.encode("base64")
        return self.write(cr, uid, ids, {'state': 'end', 'data': out, 'name': file_name}, context=context)
