# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2016 Didotech srl (<http://www.didotech.com>).
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
import datetime
from xlwt import *
import logging
from cStringIO import StringIO
import copy
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
import collections


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
    
    red = easyxf('font: italic off, color red, height 160, height 160; align: horiz right',
                 num_format_str=u'€#,##0.00')
    green = easyxf('font: italic off, color green, height 160; align: horiz right',
                   num_format_str=u'€#,##0.00')
    blue = easyxf('font: italic off, color blue, height 160; align: horiz right',
                  num_format_str=u'€#,##0.00')
    grey = easyxf('font: italic off, color grey_ega, height 160; align: horiz right',
                  num_format_str=u'€#,##0.00')
    black = easyxf('font: italic off, color black, height 160; align: horiz right', num_format_str=u'##0.00')
    black_currency = easyxf('font: italic off, color black, height 160; align: horiz right', num_format_str=u'€#,##0.00')
    red_on_yellow = easyxf('font: italic off, color red, height 160; pattern: pattern solid, fore-colour yellow; align: horiz right',
                           num_format_str=u'€#,##0.00')
    green_on_yellow = easyxf('font: italic off, color green, height 160; pattern: pattern solid, fore-colour yellow; align: horiz right',
                             num_format_str=u'€#,##0.00')
    blue_on_yellow = easyxf('font: italic off, color blue, height 160; pattern: pattern solid, fore-colour yellow; align: horiz right',
                            num_format_str=u'€#,##0.00')
    black_on_grey = easyxf('font: italic off, height 160; pattern: pattern solid, fore-colour grey25',
                           num_format_str=u'€#,##0.00')
    black_on_yellow = easyxf('font: italic off, height 160; pattern: pattern solid, fore-colour yellow',
                             num_format_str=u'€#,##0.00')
    yellow_on_grey = easyxf('font: italic off, color yellow, height 160; pattern: pattern solid, fore-colour grey25; align: horiz center; borders: top thin, bottom thin, left thin, right thin',
                            num_format_str=u'€#,##0.00')
    blue_on_blue = easyxf('font: italic off, color blue, height 160; pattern: pattern solid, fore-colour 0x29; align: horiz center; borders: top thin, bottom thin, left thin, right thin',
                          num_format_str=u'€#,##0.00')
    
    blue_with_borders = copy.deepcopy(blue)
    blue_with_borders.num_format_str = u'0.0%'
    blue_with_borders.borders = Borders()
    blue_with_borders.borders.left = 1
    blue_with_borders.borders.right = 1
    blue_with_borders.borders.top = 1
    blue_with_borders.borders.bottom = 1
    
    red_with_border = copy.deepcopy(red)
    red_with_border.borders = Borders()
    red_with_border.borders.left = 1
    red_with_border.borders.right = 1
    
    kit_red_with_border = easyxf('font: italic off, color red, height 160, height 160; align: horiz right; pattern: pattern solid, fore-colour gold; borders: left thin, right thin',
                                 num_format_str=u'€#,##0.00')
    
    kit_grey_with_border = easyxf('font: italic off, color grey_ega, height 160, height 160; align: horiz right; pattern: pattern solid, fore-colour gold; borders: left thin, right thin',
                                  num_format_str=u'#,##0.00')
    
    kit_green_with_border = easyxf('font: italic off, color green, height 160, height 160; align: horiz right; pattern: pattern solid, fore-colour gold; borders: left thin, right thin',
                                   num_format_str=u'€#,##0.00')
    
    grey_with_border = copy.deepcopy(grey)
    grey_with_border.num_format_str = u'0.0'
    grey_with_border.borders = Borders()
    grey_with_border.borders.left = 1
    grey_with_border.borders.right = 1
    
    green_with_border = copy.deepcopy(green)
    green_with_border.borders = Borders()
    green_with_border.borders.left = 1
    green_with_border.borders.right = 1

    black_with_border = copy.deepcopy(black)
    black_with_border.borders = Borders()
    black_with_border.borders.left = 1
    black_with_border.borders.right = 1
    
    
class WizardExportProjectCost(orm.TransientModel):
    '''
    If price_unit == list_price:
        line.discount -> excel.discount
    else:
        if calculated discount == line.pricelist_discount:
            line.pricelist_discount -> excel.discount
        else:
            if line.pricelist_discount:
                
            else:
                calculated discount -> excel.discount or margin
                
        (?) line.discount should be calculated or price_unit updated
    '''
    
    _name = "wizard.export.project.cost"
    _description = 'Download Project Cost'

    _columns = {
        'data': fields.binary("File", readonly=True),
        'name': fields.char('Filename', 32, readonly=True),
        'date_from': fields.date("Date from"),
        'date_to': fields.date("Date to"),
        'state': fields.selection((
            ('choose', 'choose'),   # choose
            ('get', 'get'),         # get the file
        )),
    }

    _defaults = {
        'state': lambda *a: 'choose',
    }

    table_layout = collections.OrderedDict({
        0: {'name': 'Commessa', 'width': 4000, 'header': Style.main, 'row': Style.main_cell, 'kit_header': Style.kit_main_cell_left, 'kit': Style.kit_main_cell_left},
        1: {'name': 'km auto Prev', 'width': 3500, 'header': Style.main, 'row': Style.black, 'kit_header': Style.kit_main_cell_left, 'kit': Style.kit_main_cell_left},
        2: {'name': 'km auto', 'width': 3500, 'header': Style.main, 'row': Style.black, 'kit_header': Style.kit_main_cell_left, 'kit': Style.kit_main_cell_left},
        3: {'name': 'ORE Tenico Prev', 'width': 3500, 'header': Style.main, 'row': Style.black, 'kit_header': Style.kit_main_cell_left, 'kit': Style.kit_main_cell_left},
        4: {'name': 'ORE Tenico', 'width': 3500, 'header': Style.main, 'row': Style.black, 'kit_header': Style.kit_main_cell_left, 'kit': Style.kit_main_cell_left},
        5: {'name': 'Pernottamenti Prev', 'width': 3500, 'header': Style.main, 'row': Style.black_currency, 'kit_header': Style.kit_main_cell_left, 'kit': Style.kit_main_cell_left},
        6: {'name': 'Pernottamenti', 'width': 3500, 'header': Style.main, 'row': Style.black_currency, 'kit_header': Style.kit_main_cell_left, 'kit': Style.kit_main_cell_left},
        7: {'name': 'Pranzi/Cene Prev', 'width': 3500, 'header': Style.main, 'row': Style.black_currency, 'kit_header': Style.kit_main_cell_left, 'kit': Style.kit_main_cell_left},
        8: {'name': 'Pranzi/Cene', 'width': 3500, 'header': Style.main, 'row': Style.black_currency,
            'kit_header': Style.kit_main_cell_left, 'kit': Style.kit_main_cell_left},
    })
    
    def write_header(self, ws, sale_order):
        row = 2

        for column, value in self.table_layout.iteritems():
            h_style = copy.copy(value['header'])
            h_style.borders = Borders()
            h_style.borders.bottom = 1
            ws.write(row, column, value['name'], h_style)
        ws.set_panes_frozen(True)  # frozen headings instead of split panes
        row += 1
        ws.set_horz_split_pos(row)  # in general, freeze after last heading row
        ws.set_remove_splits(True)  # if user does unfreeze, don't leave a split there
        
        for column, value in self.table_layout.iteritems():
            ws.write(row, column, '', Style.black_on_grey)
        
        return ws, row
    
    def write_row(self, ws, row, values, style):
        for column, value in values.iteritems():
            ws.write(row, column, value, self.table_layout[column][style])

    def export_sale_order(self, cr, uid, ids, context={}):

        name = u'Project'  # context.get('name', 'Project').replace(' ', '_')
        file_name = 'report_{0}_{1}.xls'.format(name, datetime.datetime.now().strftime('%Y-%m-%d'))
        account_analytic_line_obj = self.pool['account.analytic.line']
        book = Workbook(encoding='utf-8')
        ws = book.add_sheet(name)
        export_wizard = self.browse(cr, uid, ids, context)[0]
        date_start = export_wizard.date_from
        date_stop = export_wizard.date_to

        for index, column in self.table_layout.iteritems():
            ws.col(index).width = column['width']
        
        project_ids = context.get('active_ids', False)
        sale_order_obj = self.pool['sale.order']
        sale_order_line_obj = self.pool['sale.order.line']
        sale_order_line_mrp_bom_obj = self.pool['sale.order.line.mrp.bom']

        projects = self.pool['project.project'].browse(cr, uid, project_ids, context)
        
        column = 0
        row = 0
        
        ws, row = self.write_header(ws, projects)
        
        row += 1

        for row, project in enumerate(projects, row):
            if date_start and date_stop:
                domain = ['&', ('account_id', '=', project.analytic_account_id.id),
                          ('date', '>', date_start), ('date', '<', date_stop), ('product_id.type', '=', 'service')]
            else:
                domain = ['&', ('account_id', '=', project.analytic_account_id.id), ('product_id.type', '=', 'service')]

            analytic_ids = account_analytic_line_obj.search(cr, uid, domain, context=context)
            km_auto = 0
            ore_tenico = 0
            pernottamenti = 0
            pranzi_cene = 0
            km_auto_sale = 0
            ore_tenico_sale = 0
            pernottamenti_sale = 0
            pranzi_cene_sale = 0

            for line in account_analytic_line_obj.browse(cr, uid, analytic_ids, context):
                if line.product_id.code == 'KM':
                    km_auto += line.unit_amount
                elif line.product_id.code == 'ORE':
                    ore_tenico += line.unit_amount
                elif line.product_id.code == 'PERNOT':
                    pernottamenti += line.amount
                elif line.product_id.code == 'PRANZI/CENE':
                    pranzi_cene += line.amount

            name = project.name.split('-')[0].replace(' ', '')
            sale_order_ids = sale_order_obj.search(cr, uid, [('name', 'ilike', name)], context=context)
            sale_order_line_ids = sale_order_line_obj.search(cr, uid, [('order_id', 'in', sale_order_ids)], context=context)
            sale_order_line_mrp_bom_ids = sale_order_line_mrp_bom_obj.search(cr, uid, [('order_id', 'in', sale_order_line_ids)], context=context)
            for line in sale_order_line_mrp_bom_obj.browse(cr, uid, sale_order_line_mrp_bom_ids, context):
                if line.product_id.code == 'KM':
                    km_auto_sale += line.product_uom_qty
                elif line.product_id.code == 'ORE':
                    ore_tenico_sale += line.product_uom_qty
                elif line.product_id.code == 'PERNOT':
                    pernottamenti_sale += line.price_subtotal
                elif line.product_id.code == 'PRANZI/CENE':
                    pranzi_cene_sale += line.price_subtotal

            xls_line = {
                0: project.name,
                1: int(abs(km_auto_sale)),
                2: int(abs(km_auto)),
                3: int(abs(ore_tenico_sale)),
                4: int(abs(ore_tenico)),
                5: abs(pernottamenti_sale),
                6: abs(pernottamenti),
                7: abs(pranzi_cene),
                8: abs(pranzi_cene_sale),
            }
            self.write_row(ws, row, xls_line, 'row')

        """PARSING DATA AS STRING """
        file_data = StringIO()
        book.save(file_data)
        """STRING ENCODE OF DATA IN WKSHEET"""
        out = file_data.getvalue()
        out = out.encode("base64")
        return self.write(cr, uid, ids, {'state': 'get', 'data': out, 'name': file_name}, context=context)
