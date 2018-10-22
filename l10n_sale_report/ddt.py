# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2014 Didotech SRL
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
import re
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'raggruppa': self._raggruppa,
            'raggruppaddt': self._raggruppaddt,
            'righe': self._righe,
            'righeddt': self._righeddt,
            'indirizzo': self._indirizzo,
            'div': self._div,
            'italian_number': self._get_italian_number,
            'pallet_sum': self._get_pallet_sum,
            'get_description': self._get_description,
            'get_reference': self._get_reference,
            'desc_nocode': self._desc_nocode,
            'utente': self._get_utente,
            'raggruppa_sale_line': self._raggruppa_sale_line,
            'righe_sale_line': self._righe_sale_line,
            'get_description_line': self._get_description_line,
            'get_full_delivery': self._get_full_delivery,
            'today': self._get_today,
            'raggruppa_righe_prodotto': self._raggruppa_righe_prodotto,
            'spese_incasso': self._get_spese_incasso,
            'delivery_cost': self._get_delivery_cost,
        })
        self.context = context
        self.product_line = {}
        self.delivery_cost = False
        self.spese_incasso = False

    def _get_spese_incasso(self, lines):
        if self.spese_incasso:
            return self.spese_incasso
        excluse_product_ids = self.pool['account.payment.term'].get_product_incasso(self.cr, self.uid, self.context)
        spese_incasso = 0.0
        for line in lines:
            if line.product_id and line.product_id.id in excluse_product_ids:
                spese_incasso += line.price_subtotal
        self.spese_incasso = spese_incasso
        return spese_incasso

    def _get_delivery_cost(self, order_line):
        if self.delivery_cost:
            return self.delivery_cost

        delivery_product = []
        delivery_ids = self.pool['delivery.carrier'].search(self.cr, self.uid, [('product_id', '!=', False)], context=self.context)
        for delivery in self.pool['delivery.carrier'].browse(self.cr, self.uid, delivery_ids, self.context):
            if delivery.product_id.id not in delivery_product:
                delivery_product.append(delivery.product_id.id)
        delivery_cost = 0
        for line in order_line:
            if line.product_id and line.product_id.id in delivery_product:
                delivery_cost += line.price_unit
        self.delivery_cost = delivery_cost
        return delivery_cost

    def _get_today(self):
        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        return today

    def _get_full_delivery(self, object):
        stock_picking_obj = self.pool['stock.picking']
        res = ''
        if object:
            picking_ids = stock_picking_obj.search(self.cr, self.uid, [('origin', '=', object.origin), ('state', 'not in', ['cancel'])], order="id", context=self.context)
            if (len(picking_ids) == 1) or picking_ids[0] == object.id:
                res = 'Saldo Ordine'
            else:
                res = 'Evasione Parziale'
        return res

    def _get_reference(self, order_name):
        order_obj = self.pool['sale.order']
        description = []
        if order_name:
            order_ids = order_obj.search(self.cr, self.uid, [('name', '=', order_name)], context=self.context)
            if len(order_ids) == 1:
                order = order_obj.browse(self.cr, self.uid, order_ids[0], self.context)
                if order.client_order_ref:
                    order_date = datetime.strptime(order.date_order, DEFAULT_SERVER_DATE_FORMAT)
                    description.append(u'{client_order} of {customer_order_date}'.format(client_order=order.client_order_ref, customer_order_date=order_date.strftime("%m/%d/%Y")))
        return '\n'.join(description)

    def _get_utente(self):
        res = self.pool['res.users'].browse(self.cr, self.uid, self.uid)
        return res

    def _desc_nocode(self, string):
        return re.compile('\[.*\]\ ').sub('', string)

    def _raggruppa_righe_prodotto(self, stock_move):
        if self.product_line:
            return self.product_line
        product_line = {}
        for line in stock_move:
            if line.product_id not in product_line.keys():
                product_line[line.product_id] = []
            product_line[line.product_id].append(line)
        self.product_line = product_line
        return product_line

    def _raggruppa_sale_line(self, righe_ddt):
        indice_movimenti = {}
        movimenti_filtrati = []
        for riga in righe_ddt:
            if not riga.sale_line_id in indice_movimenti:
                indice_movimenti[riga.sale_line_id] = riga.sale_line_id
                movimenti_filtrati.append(riga)
        return movimenti_filtrati

    def _righe_sale_line(self, righe_ddt, filtro):
        righe_filtrate = []
        for riga in righe_ddt:
            if riga.sale_line_id == filtro.sale_line_id:
                righe_filtrate.append(riga)
        return righe_filtrate

    def _get_description_line(self, object):
        res = False
        return res

        
    def _get_description(self, order_name):
        order_obj = self.pool['sale.order']
        description = []

        if order_name and not self.pool['res.users'].browse(
                self.cr, self.uid, self.uid, self.context).company_id.disable_sale_ref_invoice_report:
            order_ids = order_obj.search(self.cr, self.uid, [('name', '=', order_name)], context=self.context)
            if len(order_ids) == 1:
                order = order_obj.browse(self.cr, self.uid, order_ids[0], self.context)
                order_date = datetime.strptime(order.date_order, DEFAULT_SERVER_DATE_FORMAT)
                if order.client_order_ref:
                    description.append(u'Rif. Ns. Ordine {order} del {order_date}, Vs. Ordine {client_order}'.format(order=order.name, order_date=order_date.strftime("%d/%m/%Y"), client_order=order.client_order_ref))
                else:
                    description.append(u'Rif. Ns. Ordine {order} del {order_date}'.format(order=order.name, order_date=order_date.strftime("%d/%m/%Y")))

        return ' / '.join(description)

    def _div(self, up, down):
        res = 0
        if down:
            res = up / down
        return res

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

    def _raggruppa(self, righe_fattura):
        indice_movimenti = {}
        movimenti_filtrati = []
        for riga in righe_fattura:
            if riga.origin in indice_movimenti and riga.origin in indice_movimenti[riga.origin]:
                print riga
                print riga.origin
            else:
                if riga.origin:
                    print 'Riga Buona'
                    if riga.ddt_origin in indice_movimenti:
                        indice_movimenti[riga.ddt_origin][riga.sale_origin] = riga.sale_origin
                    else:
                        indice_movimenti[riga.ddt_origin] = {riga.sale_origin: riga.sale_origin}
                    movimenti_filtrati.append(riga)
                else:
                    continue
        print indice_movimenti
        print movimenti_filtrati
        return movimenti_filtrati

    def _righe(self, righe_fattura, filtro):
        righe_filtrate = []
        print filtro
        print righe_fattura
        for riga in righe_fattura:
            if ((riga.origin == filtro.origin)):
                righe_filtrate.append(riga)
        return righe_filtrate

    def _raggruppaddt(self, righe_ddt):
        indice_movimenti = {}
        movimenti_filtrati = []
        print righe_ddt
        for riga in righe_ddt:
            if riga.origin in indice_movimenti:
                print riga.origin
            else:
                indice_movimenti[riga.origin] = riga.origin
                movimenti_filtrati.append(riga)
        print indice_movimenti
        return movimenti_filtrati

    def _righeddt(self, righe_ddt, filtro):
        righe_filtrate = []
        print filtro
        print righe_ddt
        for riga in righe_ddt:
            if riga.origin == filtro.origin:
                righe_filtrate.append(riga)
        return righe_filtrate

    def _indirizzo(self, partner):
        address = self.pool['res.partner'].address_get(self.cr, self.uid, [partner.id], ['default', 'invoice'])
        return self.pool['res.partner.address'].browse(self.cr, self.uid, address['invoice'] or address['default'])

    def _get_pallet_sum(self, product_ul_id, partner_id):
        pallet_sum = self.pool['product.ul'].get_pallet_sum(
            self.cr, self.uid, [product_ul_id], 'pallet_sum', None, context={'partner_id': partner_id}
        )
        return pallet_sum[product_ul_id]
