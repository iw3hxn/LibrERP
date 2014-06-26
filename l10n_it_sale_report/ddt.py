# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
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
        })

    def _div(self, up, down):
        res = 0
        if down:
            res=up/down
        return res
 
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
              if indice_movimenti.has_key(riga.ddt_origin):
                indice_movimenti[riga.ddt_origin][riga.sale_origin] = riga.sale_origin
              else:
                indice_movimenti[riga.ddt_origin] = {riga.sale_origin:riga.sale_origin}

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
            indice_movimenti[riga.origin]=riga.origin
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
        address = self.pool['res.partner'].address_get(self.cr, self.uid, [partner.id],['default', 'invoice'])
        return self.pool['res.partner.address'].browse(self.cr, self.uid, address['invoice'] or address['default'])



