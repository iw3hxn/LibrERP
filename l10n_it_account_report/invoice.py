# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2014 Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from core_extended.ordereddict import OrderedDict
from openerp.osv import orm
from openerp.tools.translate import _


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'invoice_tree': self._get_invoice_tree,
            'italian_number': self._get_italian_number,
            'invoice_move_lines': self._get_invoice_move_lines,
            'ddt': self._get_ddt,
            'set_picking': self._set_picking,
            'indirizzo': self._indirizzo,
            'div': self._div,
        })
        
        self.cache = {}

    #def _get_ddt(self):
    #    return self.pool.get('stock.picking').browse(self.cr, self.uid,
    #                                                 self.localcontext['data']['form']['picking_id'])
    
    def _div(self, up, down):
        res = 0
        #import pdb; pdb.set_trace()
        if down:
            res = up / down
        return res
    
    def _set_picking(self, invoice):
        self._get_invoice_tree(invoice.invoice_line)
        return False
    
    def _get_ddt(self):
        def get_picking(picking_name):
            picking_ids = self.pool['stock.picking'].search(self.cr, self.uid, [('name', '=', picking_name)])
            if picking_ids:
                return self.pool['stock.picking'].browse(self.cr, self.uid, picking_ids[0])
        invoice = self.pool['account.invoice'].browse(self.cr, self.uid, self.ids[0])
        if hasattr(invoice, 'move_products') and invoice.move_products:
            return self.pool['account.invoice'].browse(self.cr, self.uid, self.ids[0])
        if hasattr(self, 'picking_name'):
            return self.cache.get(self.picking_name, False) or self.cache.setdefault(self.picking_name, get_picking(self.picking_name))
        return False

    def _get_italian_number(self, number, precision=2, no_zero=False):
        if not number and no_zero:
            return ''
        elif not number:
            return '0,00'

        if number < 0:
            sign = '-'
        else:
            sign = ''
        ## Requires Python >= 2.7:
        #before, after = "{:.{digits}f}".format(number, digits=precision).split('.')
        ## Works with Python 2.6:
        if precision:
            before, after = "{0:10.{digits}f}".format(number, digits=precision).strip('- ').split('.')
        else:
            before = "{0:10.{digits}f}".format(number, digits=precision).strip('- ').split('.')[0]
            after = ''
        belist = []
        end = len(before)
        for i in range(3, len(before) + 3, 3):
            start = len(before) - i
            if start < 0:
                start = 0
            belist.append(before[start: end])
            end = len(before) - i
        before = '.'.join(reversed(belist))
        
        if no_zero and int(number) == float(number) or precision == 0: 
            return sign + before
        else:
            return sign + before + ',' + after
    
    def get_description(self, ddt_name, order_name):
        ddt_obj = self.pool.get('stock.picking')
        order_obj = self.pool.get('sale.order')
        description = []
        if ddt_name:
            ddt_ids = ddt_obj.search(self.cr, self.uid, [('name', '=', ddt_name)])
            if len(ddt_ids) == 1:
                ddt = ddt_obj.browse(self.cr, self.uid, ddt_ids[0])
                if ddt.ddt_number:
                    ddt_date = datetime.strptime(ddt.ddt_date, DEFAULT_SERVER_DATE_FORMAT)
                    ## Ex: Rif. Ns. DDT 2012/0335
                    description.append(u'Rif. Ns. DDT {ddt} del {ddt_date}'.format(ddt=ddt.ddt_number, ddt_date=ddt_date.strftime("%d/%m/%Y")))
        
        if order_name and not self.pool['res.users'].browse(
                self.cr, self.uid, self.uid).company_id.disable_sale_ref_invoice_report:
            order_ids = order_obj.search(self.cr, self.uid, [('name', '=', order_name)])
            if len(order_ids) == 1:
                order = order_obj.browse(self.cr, self.uid, order_ids[0])
                order_date = datetime.strptime(order.date_order, DEFAULT_SERVER_DATE_FORMAT)
                description.append(u'Rif. Ns. Ordine {order} del {order_date}'.format(order=order.name, order_date=order_date.strftime("%d/%m/%Y")))
            
        return ' / '.join(description)
    
    def _get_picking_name(self, line):
        picking_obj = self.pool['stock.picking']
        picking_ids = picking_obj.search(self.cr, self.uid, [('origin', '=', line.origin)])
        
        if len(picking_ids) == 1:
            picking = picking_obj.browse(self.cr, self.uid, picking_ids[0])
            return picking.name
        elif picking_ids:
            move_obj = self.pool['stock.move']
            move_ids = move_obj.search(self.cr, self.uid, [('product_id', '=', line.product_id.id), ('origin', '=', line.origin)])
            if len(move_ids) == 1:
                stock_move = move_obj.browse(self.cr, self.uid, move_ids[0])
                if stock_move.picking_id:
                    return stock_move.picking_id.name
                else:
                    return False
            elif move_ids:
                # The same product from the same sale_order is present in various picking lists
                raise orm.except_orm('Warning', _('Ambiguous line origin'))
                
                #stock_moves = move_obj.browse(self.cr, self.uid, move_ids)
                #picking_names = []
                #for stock_move in stock_moves:
                #    if stock_move.picking_id:
                #        picking_names.append(stock_move.picking_id.name)
                #
                #if picking_names:
                #    if len(picking_names) == 1:
                #        picking_names[0]
                #    else:
                #        return picking_names
                #else:
                #    return False
            else:
                return False
        else:
            return False
    
    def _get_invoice_tree(self, invoice_lines):
        invoice = {}
        keys = {}
        picking_obj = self.pool['stock.picking']
        for line in invoice_lines:
            if line.origin:
                if ':' in line.origin:
                    split_list = line.origin.split(':')
                    ddt, sale_order = split_list[0], split_list[1]
                    if line.invoice_id.direct_invoice:
                        self.picking_name = ddt
                        ddt = False
                elif line.origin[:4] == 'OUT/':
                    if line.invoice_id.direct_invoice:
                        self.picking_name = line.origin
                        ddt = False
                    else:
                        ddt = line.origin
                    sale_order = False
                elif line.origin[:4] == 'IN/':
                    ddt = False
                    sale_order = False
                elif line.invoice_id.direct_invoice:
                    print line.origin
                    ddt = False
                    sale_order = line.origin
                    self.picking_name = self._get_picking_name(line)
                    #if isinstance(self.picking_name, (list, tuple)):
                else:
                    ddt = False
                    sale_order = line.origin
            else:
                ddt = False
                sale_order = False
            
            # Order lines by date and by ddt, so first create date_ddt key:
            if ddt and ddt in keys:
                key = keys[ddt]
            elif ddt:
                picking_ids = picking_obj.search(self.cr, self.uid, [('name', '=', ddt)])
                if picking_ids:
                    picking = picking_obj.browse(self.cr, self.uid, picking_ids[0])
                    key = "{0}_{1}".format(picking.ddt_date, ddt)
                else:
                    key = ddt
            else:
                key = False
            
            if key in invoice:
                invoice[key]['lines'].append(line)
            else:
                description = self.get_description(ddt, sale_order)
                invoice[key] = {'description': description, 'lines': [line]}
        
        return OrderedDict(sorted(invoice.items(), key=lambda t: t[0])).values()

    def _get_invoice_move_lines(self, move_id):
        if move_id.line_id:
            return [line for line in move_id.line_id if line.date_maturity]
        else:
            return []

    def _indirizzo(self, partner):
        address = self.pool['res.partner'].address_get(self.cr, self.uid, [partner.id], ['default', 'invoice'])
        return self.pool['res.partner.address'].browse(self.cr, self.uid, address['invoice'] or address['default'])

