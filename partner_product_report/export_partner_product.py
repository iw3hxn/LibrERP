# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2015-2016 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
import datetime
from dateutil.relativedelta import relativedelta
from xlwt import Workbook, Borders, easyxf
import logging
from cStringIO import StringIO
import copy
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
import collections
import calendar
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class Style:
    main = easyxf('font: height 160; align: horiz center')
    main_small = easyxf('font: height 120; align: horiz center; borders: left thin, right thin')
    main_with_borders = easyxf('font: height 120; align: horiz center; borders: top thin, bottom thin, left thin, right thin')

    main_cell = easyxf('font: height 160; align: horiz center; borders: left thin, right thin')
    kit_main_cell = easyxf('font: height 160; pattern: pattern solid, fore-colour gold; align: horiz center; borders: left thin, right thin')
    main_cell_left = main_cell = easyxf('font: height 160; align: horiz left; borders: left thin, right thin')
    kit_main_cell_left = easyxf('font: height 160; pattern: pattern solid, fore-colour gold; align: horiz left; borders: left thin, right thin')
    
    euro = copy.deepcopy(main)
    euro.num_format_str = u'"€"#,##0.00'
    kit_euro = copy.deepcopy(kit_main_cell)
    kit_euro.num_format_str = u'"€"#,##0.00'

    dirham = copy.deepcopy(main)
    dirham.num_format_str = u'"AED" #,##0.00'

    ##  6*0x14 = 120
    ##  8*0x14 = 160
    ## 10*0x14 = 200
    ## 12*0x14 = 240
    ## 14*0x14 = 280
    modello = easyxf('font: bold on, height 200')
    
    bold = easyxf('font: bold on, height 160; align: horiz center')
    
    bold_border = copy.deepcopy(bold)
    bold_border.num_format_str = u'0.0'
    bold_border.borders.left = 1
    bold_border.borders.right = 1
    bold_border.borders.top = 1
    bold_border.borders.bottom = 1

    grey = easyxf('font: italic off, color grey_ega, height 160; align: horiz right',
                  num_format_str=u'€#,##0.00')
    black_on_grey = easyxf('font: italic off, height 160; pattern: pattern solid, fore-colour grey25',
                           num_format_str=u'€#,##0.00')

    grey_with_border = copy.deepcopy(grey)
    
    
class WizardExportPartnerProduct(orm.TransientModel):
    _name = "wizard.export.partner.product"
    _description = 'Download Partner Product'

    def get_years(self, cr, uid, context):
        cr.execute("""SELECT TO_CHAR(s_order.date_order, 'YYYY') AS year
            FROM sale_order_line AS line
            LEFT JOIN sale_order AS s_order ON line.order_id=s_order.id
            WHERE s_order.state IN ('confirmed', 'progress', 'done')
            GROUP BY year
        """)
        years = []
        for row in cr.dictfetchall():
            years.append((row['year'], row['year']))

        return years

    _columns = {
        'data': fields.binary("File", readonly=True),
        'name': fields.char('Filename', 64, readonly=True),
        'state': fields.selection((
            ('choose', 'choose'),   # choose
            ('get', 'get'),         # get the file
        )),
        'year': fields.selection(get_years, _('Year'), required=True)
    }

    _defaults = {
        'state': lambda *a: 'choose',
    }

    table_layout = collections.OrderedDict({
        0: {'name': u'#', 'width': 1000, 'header': Style.bold_border, 'row': Style.main_cell},
        1: {'name': 'Agente', 'width': 2600, 'header': Style.bold_border, 'row': Style.main_cell},
        2: {'name': 'Zona', 'width': 2500, 'header': Style.bold_border, 'row': Style.main_cell},
        3: {'name': 'Tipologia Cliente', 'width': 4000, 'header': Style.bold_border, 'row': Style.main_cell},
        4: {'name': 'Area Manager', 'width': 4000, 'header': Style.bold_border, 'row': Style.main_cell_left},

        5: {'name': 'Cliente', 'width': 7000, 'header': Style.bold_border, 'row': Style.main_cell_left},
        6: {'name': u'Nazionalità Cliente', 'width': 4500, 'header': Style.bold_border, 'row': Style.main},
        7: {'name': 'Sede di Consegna', 'width': 5000, 'header': Style.bold_border, 'row': Style.main_cell},
        8: {'name': 'Gruppo Prodotto', 'width': 7000, 'header': Style.bold_border, 'row': Style.main_cell},
        9: {'name': 'Sottogruppo Prodotto', 'width': 5000, 'header': Style.bold_border, 'row': Style.main_cell},
        10: {'name': 'Cod. Articolo', 'width': 3000, 'header': Style.bold_border, 'row': Style.main_cell},
    })

    for column in range(11, 83, 6):
        table_layout.update({
            column: {'name': u'Qtà venduta', 'width': 3000, 'header': Style.main, 'row': Style.main},
            column + 1: {'name': 'Prezzo Listino', 'width': 3000, 'header': Style.main, 'row': Style.dirham},
            column + 2: {'name': 'Prezzo vendita', 'width': 3000, 'header': Style.main, 'row': Style.dirham},
            column + 3: {'name': 'Costo DB', 'width': 3000, 'header': Style.main, 'row': Style.dirham},
            column + 4: {'name': 'Provvigioni', 'width': 3000, 'header': Style.main, 'row': Style.dirham},
            column + 5: {'name': 'Condiz. Pagamento (GG)', 'width': 5000, 'header': Style.main, 'row': Style.main_cell_left},
        })

    def get_address(self, cr, uid, partner_id, address_type, context):
        address_obj = self.pool['res.partner.address']

        if address_type == 'any':
            address_ids = address_obj.search(cr, uid, [('partner_id', '=', partner_id)])
        else:
            address_ids = address_obj.search(cr, uid, [('partner_id', '=', partner_id), ('type', '=', address_type)])

        if address_ids:
            return address_obj.browse(cr, uid, address_ids[0], context)
        elif address_type == 'default':
            return self.get_address(cr, uid, partner_id, 'any', context)
        elif address_type == 'any':
            return False
        else:
            return self.get_address(cr, uid, partner_id, 'default', context)

    def write_header(self, ws, year):
        row = 0

        for column in range(0, 11):
            ws.write(row, column, '', Style.black_on_grey)

        for month, column in enumerate(range(11, 83, 6), 1):
            for shift in range(0, 6):
                ws.write(row, column + shift, '{} {}'.format(calendar.month_abbr[month], year), Style.main)

        row = 1
        
        for column, value in self.table_layout.iteritems():
            h_style = copy.copy(value['header'])
            h_style.borders = Borders()
            h_style.borders.bottom = 1
            ws.write(row, column, value['name'], h_style)
        ws.set_panes_frozen(True)  # frozen headings instead of split panes

        return ws, row

    def write_row(self, ws, row, values, style):
        for column, value in values.iteritems():
            ws.write(row, column, value, self.table_layout[column][style])

        return ws

    def get_month_start_end(self, month, year):
        date_start = datetime.date(year, month, 1)
        date_end = date_start + relativedelta(months=1) - relativedelta(days=1)
        return date_start.strftime(DEFAULT_SERVER_DATE_FORMAT), date_end.strftime(DEFAULT_SERVER_DATE_FORMAT)

    def get_month_query(self, month, year):
        date_start, date_end = self.get_month_start_end(month, year)

        return """SELECT s_order.partner_id, line.product_id, SUM(product_uom_qty) AS qty
            FROM sale_order_line AS line
            LEFT JOIN sale_order AS s_order ON line.order_id=s_order.id
            LEFT JOIN res_partner AS partner ON s_order.partner_id=partner.id
            LEFT JOIN product_product AS product ON line.product_id=product.id
            LEFT JOIN product_template AS template ON product.product_tmpl_id=template.id
            WHERE s_order.state IN ('confirmed', 'progress', 'done')
            AND s_order.date_order >= '{start}'
            AND s_order.date_order <= '{end}'
            AND s_order.active = 'true'
            GROUP BY s_order.partner_id, line.product_id
        """.format(start=date_start, end=date_end)

    def export_partner_product(self, cr, uid, ids, context={}):
        report = self.browse(cr, uid, ids[0], context)

        name = context.get('name', 'Partner-Product')
        file_name = 'report_{0}_{1}.xls'.format(name, datetime.datetime.now().strftime('%Y-%m-%d'))

        book = Workbook(encoding='utf-8')
        #ws = book.add_sheet(name, cell_overwrite_ok=True)
        ws = book.add_sheet(name)

        for index, column in self.table_layout.iteritems():
            ws.col(index).width = column['width']

        ws, row_number = self.write_header(ws, report.year)

        # partner_ids = self.pool['res.partner'].search(cr, uid, [])
        # partners = self.pool['res.partner'].browse(cr, uid, partner_ids, context)
        #
        # partners = {partner.id: partner for partner in partners}

        row_number += 1

        query = """
            SELECT partner.name, product.name_template, s_order.partner_id, line.product_id, product.default_code, SUM(product_uom_qty)
            FROM sale_order_line AS line
            LEFT JOIN sale_order AS s_order ON line.order_id=s_order.id
            LEFT JOIN res_partner AS partner ON s_order.partner_id=partner.id
            LEFT JOIN product_product AS product ON line.product_id=product.id
            WHERE s_order.state IN ('confirmed', 'progress', 'done')
            AND s_order.date_order >= '{year}-01-01'
            AND s_order.date_order <= '{year}-12-31'
            AND s_order.active = 'true'
            GROUP BY s_order.partner_id, line.product_id, partner.name, product.name_template, product.default_code
            ORDER BY partner.name
        """.format(year=report.year)

        cr.execute(query)
        results = cr.dictfetchall()

        report_table = collections.OrderedDict({})

        for row in results:
            if not row['partner_id'] in report_table:
                report_table[row['partner_id']] = collections.OrderedDict({})

            report_table[row['partner_id']][row['product_id']] = row

        for month in range(1, 13):
            month_query = self.get_month_query(month, int(report.year))

            cr.execute(month_query)
            month_results = cr.dictfetchall()

            for row in month_results:
                report_table[row['partner_id']][row['product_id']][month] = row

        for partner_id, partner_data in report_table.items():
            partner_address = self.get_address(cr, uid, partner_id, 'default', context)
            partner_delivery_address = self.get_address(cr, uid, partner_id, 'delivery', context)
            for product_id, product_row in partner_data.items():
                if not product_id:
                    continue
                product = self.pool['product.product'].browse(cr, uid, product_id, context)

                xls_row = {
                    0: row_number + 1,
                    1: '',
                    2: '',
                    3: '',
                    4: '',
                    5: product_row['name'],  # Partner
                    6: partner_address.country_id and partner_address.country_id.name or '',
                    7: partner_delivery_address.country_id and partner_delivery_address.country_id.name or '',
                    8: product.product_tmpl_id.categ_id and product.product_tmpl_id.categ_id.name or '',  # Product
                    # 9: '',  # subcategory
                    10: product_row['default_code'],
                }

                for month, column in enumerate(range(11, 83, 6), 1):
                    if product_row.get(month) and product_row[month]['qty']:
                        date_start, date_end = self.get_month_start_end(month, int(report.year))
                        sale_order_line_ids = self.pool['sale.order.line'].search(cr, uid, [
                            ('order_id.partner_id', '=', partner_id),
                            ('product_id', '=', product_id),
                            ('order_id.date_order', '>=', date_start),
                            ('order_id.date_order', '<=', date_end)
                        ])

                        if sale_order_line_ids:
                            sale_order_line = self.pool['sale.order.line'].browse(cr, uid, sale_order_line_ids[0], context)

                            # This is not a complete check. We should also control if there is active pricelist in selected period
                            if sale_order_line.order_id.pricelist_id.version_id:
                                list_price = sale_order_line.order_id.pricelist_id.price_get(
                                    prod_id=product_id,
                                    qty=1,
                                    partner=partner_id,
                                    context={
                                        'uom': sale_order_line.product_uom.id,
                                        'date': date_start
                                    }
                                )[sale_order_line.order_id.pricelist_id.id]
                            else:
                                # print sale_order_line.order_id.name, product_row['name'], sale_order_line.order_id.pricelist_id.name
                                list_price = product.product_tmpl_id.list_price

                            user = self.pool['res.users'].browse(cr, uid, uid, context)

                            if sale_order_line.order_id.pricelist_id.currency_id.id == user.company_id.currency_id.id:
                                sale_price = sale_order_line.price_unit
                                purchase_price = sale_order_line.purchase_price
                            else:
                                sale_price = self.pool['res.currency'].compute(
                                    cr, uid,
                                    from_currency_id=sale_order_line.order_id.pricelist_id.currency_id.id,
                                    to_currency_id=user.company_id.currency_id.id,
                                    from_amount=sale_order_line.price_unit
                                )
                                purchase_price = self.pool['res.currency'].compute(
                                    cr, uid,
                                    from_currency_id=sale_order_line.order_id.pricelist_id.currency_id.id,
                                    to_currency_id=user.company_id.currency_id.id,
                                    from_amount=sale_order_line.purchase_price
                                )
                                list_price = self.pool['res.currency'].compute(
                                    cr, uid,
                                    from_currency_id=sale_order_line.order_id.pricelist_id.currency_id.id,
                                    to_currency_id=user.company_id.currency_id.id,
                                    from_amount=list_price
                                )

                            xls_row.update({
                                column: product_row.get(month) and product_row[month]['qty'] or '',
                                column + 1: list_price or '',
                                column + 2: sale_price or '',
                                column + 3: purchase_price or '',  # purchase_price
                                column + 4: '',  # Provvigioni
                                column + 5: sale_order_line.order_id.payment_term and sale_order_line.order_id.payment_term.name or ''  # payment
                            })
                        else:
                            xls_row.update({
                                column: 'Error'
                            })

                self.write_row(ws, row_number, xls_row, 'row')

                row_number += 1

        """PARSING DATA AS STRING """
        file_data = StringIO()
        book.save(file_data)
        """STRING ENCODE OF DATA IN WKSHEET"""
        out = file_data.getvalue()
        out = out.encode("base64")
        return self.write(cr, uid, ids, {'state': 'get', 'data': out, 'name': file_name}, context=context)
