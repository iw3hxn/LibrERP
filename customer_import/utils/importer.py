# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Ivan Bortolatto (ivan.bortolatto at didotech.com)
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
#

import pooler
import threading
from tools.translate import _
import math
import unicodedata

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

import xlrd

#DEBUG = True
DEBUG = False

if DEBUG:
    import pdb


class ImportFile(threading.Thread):
    def __init__(self, cr, uid, ids, context, content_text):
        # Inizializzazione superclasse
        threading.Thread.__init__(self)
        
        # Inizializzazione classe ImportPartner
        self.uid = uid
        self.dbname = cr.dbname
        self.pool = pooler.get_pool(cr.dbname)
        self.partner_obj = self.pool.get('res.partner')
        self.address_obj = self.pool.get('res.partner.address')
        self.city_obj = self.pool.get('res.city')
        self.province_obj = self.pool.get('res.province')
        self.country_obj = self.pool.get('res.country')
        self.account_obj = self.pool.get('account.account')
        self.account_type_obj = self.pool.get('account.account.type')
        self.account_fiscal_position_obj = self.pool.get('account.fiscal.position')
        self.content_text = content_text

        # Necessario creare un nuovo cursor per il thread, quello fornito dal metodo chiamante viene chiuso
        # alla fine del metodo e diventa inutilizzabile all'interno del thread.
        self.cr = pooler.get_db(self.dbname).cursor()
        self.partnerImportID = ids[0]
        
        self.context = context
        self.error = []
        self.warning = []
        self.number_row = 0

        italy_ids = self.country_obj.search(cr, uid, [('code', '=', 'IT')])
        self.italy_id = italy_ids[0]

        italy_fiscal_position_ids = self.account_fiscal_position_obj.search(cr, uid, [('name', '=', 'Italia')])
        self.italy_fiscal_position_id = italy_fiscal_position_ids[0]

        # Contatori dei nuovi partner inseriti e aggiornati, vengono utilizzati per compilare il
        # rapporto alla terminazione del processo di import
        self.uo_new = 0
        self.updated = 0
        self.problems = 0

    def run(self):
        # Recupera il record dal database
        self.filedata_obj = self.pool.get('filedata.import')
        
        self.partnerImportRecord = self.filedata_obj.browse(self.cr, self.uid, self.partnerImportID, context=self.context)
        self.file_name = self.partnerImportRecord.file_name

        book = xlrd.open_workbook(file_contents=self.content_text)
        sheet = []
        sh = book.sheet_by_index(0)

        for rx in range(sh.nrows):
            row = []
            for cx in range(sh.ncols):
                row.append(sh.cell_value(rowx=rx, colx=cx))
            sheet.append(row)

        self.numberOfLines = sh.nrows

        # Elaborazione del Cliente
        try:
            # Importa i clienti
            info = self.process(self.cr, self.uid, sheet, book.datemode)
            
            # Genera il report sull'importazione
            self.notifySuccessfulImport(info)

            # Salva le modifiche sul database e chiude la connessione
            self.cr.commit()
            self.cr.close()
        except Exception as e:
            # Annulla le modifiche fatte
            self.cr.rollback()
            self.cr.commit()
            message = "Errore alla linea %s" % self.importedLines + "\nDettaglio:\n\n" + str(e)
            
            if DEBUG:
                ### Debug
                print message
                pdb.set_trace()
            
            self.notifyError(message)

    def process(self, cr, uid, table, book_datemode):
        self.message_tittle = _("Importazione Clienti completa")
        self.importedLines = 0
        self.progressIndicator = 0
        
        notifyProgressStep = (self.numberOfLines / 100) + 1

        for row_list in table:
            # Update counter of imported lines
            # If this line generate an error we will know the right Line Number
            self.importedLines = self.importedLines + 1
            
            # Import row
            import_result = self.import_row(cr, uid, row_list, book_datemode)

            if not import_result:
                self.problems += 1

            if (self.importedLines % notifyProgressStep) == 0:
                cr.commit()
                completedQuota = float(self.importedLines) / float(self.numberOfLines)
                completedPercentage = math.trunc(completedQuota * 100)
                self.progressIndicator = completedPercentage
                self.updateProgressIndicator()

        self.progressIndicator = 100
        self.updateProgressIndicator()

    def import_row(self, cr, uid, row_list, book_datemode):
        header_list_customer = ('rag1', 'ind', 'cap', 'loc', 'prov', 'tel.', 'cell.', 'e.mail', 'cod.fisc. / partita iva', 'varie')
        self.number_row += 1

        if self.number_row == 1:
            row_str_list = [self.toStr(value) for value in row_list]
            self.problems = self.problems - 1
            for column in row_str_list:
                column_ascii = unicodedata.normalize('NFKD', column).encode('ascii', 'ignore').lower()
                if column_ascii not in header_list_customer:
                    warning = 'Riga {0}: Manca voce {1} in Testata'.format(self.importedLines, column_ascii)
                    err_string = 'Importato: ' + warning
                    _logger.debug(err_string)
                    self.warning.append(err_string)
            return

        # Sometime value is only numeric and we don't want string to be treated as Float
        temp_row_list = []
        for value in row_list:
            if isinstance(value, unicode):
                temp_value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
            else:
                temp_value = self.toStr(value)
            temp_row_list = temp_row_list + [temp_value]
        row_list = temp_row_list

        vals_input = dict((str(k), v) for k, v in zip(header_list_customer, row_list))
        
        if not vals_input['rag1']:
            warning = "Manca il valore della Ragione Sociale. La riga viene ignorata."
            err_string = u'line {0}, {1}'.format(self.importedLines, warning)
            _logger.debug(err_string)
            self.warning.append(err_string)
            return False

        # manage customers
        vals_partner = {}
        vals_partner['name'] = '%s' % (vals_input['rag1'])
        code_nations = 'IT'
        vals_partner['property_account_position'] = self.italy_fiscal_position_id
        
        if vals_input['varie'] not in ('', False, None, 0, []):
            vals_partner['comment'] = vals_input['varie']
            
        if vals_input['cod.fisc. / partita iva'] not in ('', False, None, 0, []):
            if vals_input['cod.fisc. / partita iva'].isdigit():
                if len(vals_input['cod.fisc. / partita iva']) < 11:
                    zero_add = 11 - len(vals_input['cod.fisc. / partita iva'])
                    for zero in range(0, zero_add):
                        vals_input['cod.fisc. / partita iva'] = '0' + vals_input['cod.fisc. / partita iva']
                vals_partner['vat'] = code_nations + vals_input['cod.fisc. / partita iva']
                vals_partner['fiscalcode'] = code_nations + vals_input['cod.fisc. / partita iva']
            else:
                vals_partner['fiscalcode'] = vals_input['cod.fisc. / partita iva']

        if 'vat' in vals_partner:
            if vals_partner['vat'] in ('', False, None, 0, []):
                del vals_partner['vat']
            else:
                result_check = self.partner_obj.simple_vat_check(cr, uid, code_nations, vals_partner['vat'][2:], None)
                if result_check is False:
                    warning = "Partner '{0} {1}'; Partita IVA errata: {2}. La riga viene ignorata.".format(vals_input['Codice'], vals_partner['name'], vals_partner['vat'])
                    err_string = u'line {0}, {1}'.format(self.importedLines, warning)
                    _logger.debug(err_string)
                    self.warning.append(err_string)
                    return False

        if 'vat' not in vals_partner:
            if ('fiscalcode' in vals_partner) and (len(vals_partner['fiscalcode']) == 16):
                vals_partner['individual'] = True
                
        try:
            partner_ids = self.partner_obj.search(cr, uid, [('name', '=', vals_partner['name'])])
            if partner_ids:
                if len(partner_ids) == 1:
                    partner_id = partner_ids[0]
                    self.partner_obj.write(cr, uid, partner_id, vals_partner, self.context)
                    self.updated += 1
                else:
                    error = _("Più di un Partner '{0}' trovato".format(vals_partner['name']))
                    err_string = u'line {0}, {1}'.format(self.importedLines, error)
                    _logger.debug(err_string)
                    self.error.append(err_string)
            else:
                partner_id = self.partner_obj.create(cr, uid, vals_partner, self.context)
                self.uo_new += 1
                cr.commit()
                self.partner_obj.write(cr, uid, partner_id, {'customer': True}, self.context)
        except Exception, e:
            error = _(e)
            err_string = u'line {0}, {1}\nDati: {2}'.format(self.importedLines, error, vals_partner)
            _logger.debug(err_string)
            self.error.append(err_string)
            return False

        # manage default address customer
        vals_address = {}
        if 'ind' in vals_input and vals_input['ind'] not in ('', False, None, 0, []):
            vals_address['partner_id'] = partner_id
            vals_address['type'] = 'default'
            vals_address['street'] = vals_input['ind']
            vals_address['active'] = True
            vals_address['country_id'] = self.italy_id

            if 'loc' in vals_input and vals_input['loc'] not in ('', False, None, 0, []):
                vals_address['city'] = vals_input['loc'].title()

            if 'e.mail' in vals_input and vals_input['e.mail'] not in ('', False, None, 0, []):
                vals_address['email'] = vals_input['e.mail']

            if 'tel.' in vals_input and vals_input['tel.'] not in ('', False, None, 0, []):
                tmp_tel = vals_input['tel.'].replace(' ', '')
                if tmp_tel.isdigit():
                    vals_address['phone'] = vals_input['tel.']

            if 'cell.' in vals_input and vals_input['cell.'] not in ('', False, None, 0, []):
                tmp_tel = vals_input['cell.'].replace(' ', '')
                if tmp_tel.isdigit():
                    vals_address['mobile'] = vals_input['cell.']

            if 'cap' in vals_input and vals_input['cap'] not in ('', False, None, 0, []):
                vals_address['zip'] = vals_input['cap']
            else:
                if 'city' in vals_address:
                    city_ids = self.city_obj.search(cr, uid, [('name', '=', vals_address['city'])])
                    if city_ids not in ('', False, None, 0, []):
                        city_data = self.city_obj.read(cr, uid, city_ids[0], ['zip'], None)
                        vals_address['zip'] = city_data['zip']

            if 'prov' in vals_input and vals_input['prov'] not in ('', False, None, 0, []):
                province_ids = self.province_obj.search(cr, uid, [('code', '=', vals_input['prov'].upper())])
                if province_ids not in ('', False, None, 0, []):
                    vals_address['province'] = province_ids[0]
                    province_data = self.province_obj.read(cr, uid, province_ids[0], ['region'], None)
                    vals_address['region'] = province_data['region'][0]
                
            address_ids = self.address_obj.search(cr, uid, [('partner_id', '=', vals_address['partner_id']), ('type', '=', 'default')])
            if address_ids:
                address_id = address_ids[0]
                self.address_obj.write(cr, uid, address_id, vals_address)
            else:
                address_id = self.address_obj.create(cr, uid, vals_address)
            cr.commit()

        return partner_id
        
    def notifySuccessfulImport(self, info):
        EOL = '\n<br>'
        
        body = "File '{0}' {1}{1}".format(self.file_name, EOL)
        body += _("Importate righe: {0}{1}Modificate righe: {2}{1}Righe non importate: {3}").format(self.uo_new, EOL, self.updated, self.problems)
           
        if self.error:
            body += '{0}{0}Errore:{0}'.format(EOL) + EOL.join(self.error)
            
        if self.warning:
            body += '{0}{0}Warning:{0}'.format(EOL) + EOL.join(self.warning)
        
        request = self.pool.get('res.request')
        request.create(self.cr, self.uid, {
            'name': self.message_tittle,
            'act_from': self.uid,
            'act_to': self.uid,
            'state': 'waiting',
            'body': body,
            'active': True,
        })
            
    def notifyError(self, errorDescription):
        
        body = str(errorDescription)
        request = self.pool.get('res.request')
        request.create(
            self.cr,
            self.uid,
            vals={
                'name': _("Errore importazione Customer"),
                'act_from': self.uid,
                'act_to': self.uid,
                'state': 'waiting',
                'body': body,
                'active': True,
            },
            context=self.context,
        )
            
        # Salva il messaggio di errore nel database e chiudi la connessione
        self.cr.commit()
        self.cr.close()
        
    #===========================================================================
    # Utility methods
    #===========================================================================
    def getProductTemplateID(self, product_id):
        # Get the product_tempalte ID
        
        # Retrive the record associated with the product id
        productObject = self.pool.get('product.product').browse(self.cr, self.uid, product_id)
        
        # Retrive the template id
        product_template_id = productObject.product_tmpl_id.id
        
        # Return the template id
        return product_template_id
    
    def updateProgressIndicator(self):
        self.partnerImportRecord.progress_indicator = self.progressIndicator
        self.filedata_obj.write(self.cr, self.uid, [self.partnerImportID], vals={'progress_indicator': self.progressIndicator}, context=self.context)
        print 'Import status: %d %s (%d lines processed)' % (self.progressIndicator, '%', self.importedLines)
        
    def toStr(self, value):
        if type(value) == type(u'a') or type(value) == type('a'):
            return value.strip()
        else:
            try:
                value = int(value)
            except:
                pass
            return unicode(value)


#===============================================================================
# Eccezioni
#===============================================================================
class NoProductWithSerialException(Exception):
    pass


class UnknownLocationException(Exception):
    pass
