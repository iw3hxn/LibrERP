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
from report import report_sxw


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
        })

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
        before, after = "{0:10.{digits}f}".format(number, digits=precision).strip('- ').split('.')

        belist = []
        end = len(before)
        for i in range(3, len(before) + 3, 3):
            start = len(before) - i
            if start < 0:
                start = 0
            belist.append(before[start: end])
            end = len(before) - i
        before = '.'.join(reversed(belist))

        if no_zero and int(number) == float(number):
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
        pallet_sum = self.pool['product.ul'].get_pallet_sum(self.cr, self.uid, [product_ul_id], 'pallet_sum', None, context={'partner_id': partner_id})
        return pallet_sum[product_ul_id]
