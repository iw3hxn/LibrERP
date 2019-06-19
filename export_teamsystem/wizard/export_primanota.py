# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Didotech srl (http://www.didotech.com)
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
import logging
from cStringIO import StringIO
import re
import datetime
from openerp.tools.translate import _

from openerp.addons.export_teamsystem.team_system_template import cash_book, tax_template, account_template, industrial_accounting_template
from openerp.addons.export_teamsystem.team_system_template import maturity_template, deadline_book, industrial_accounting

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

from pprint import pprint


def get_phone_number(number, prefix=''):
    phone = ''
    if number:
        if number[0] == '+':
            return {'prefix': '', 'number': ''}

        if ',' in number:
            number, other_numbers = number.split(',', 1)

        if prefix:
            if number[0] == '0':
                prefix = '0' + prefix

            if number[:len(prefix)] == prefix:
                number = number.replace(' ', '')
                phone = number[len(prefix):]

        if not phone:
            if ' ' in number:
                prefix, phone = number.split(' ', 1)
                if len(prefix) > 4:
                    number = number.replace(' ', '')
                    prefix = number[:4]
                    phone = number[4:]
            else:
                prefix = number[:4]
                phone = number[4:]

    phone = ''.join(re.findall(r'[0-9 ]*', phone))
    return {'prefix': prefix, 'number': phone}


class WizardExportPrimaNota(orm.TransientModel):
    _name = 'wizard.export.primanota.teamsystem'
    _description = "Export primanota in TeamSystem format"

    _columns = {
        'data': fields.binary("File", readonly=True),
        'name': fields.char('Filename', 64, readonly=True),
        # State of this wizard
        'state': fields.selection(
            (
                ('choose', 'choose'),
                ('end', 'end')
            ), 'state', required=True, translate=False, readonly=True
        )
    }

    _defaults = {
        'state': lambda *a: 'choose',
    }

    causal_description = {
        1: 'FATT. VENDITA',
        2: 'NOTA CREDITO',
        11: 'FATT. ACQUISTO',
        20: 'CORRISPETTIVO'
    }

    def get_phone_prefix(self, cr, uid, city, context):
        city_obj = self.pool['res.city']
        city_ids = city_obj.search(cr, uid, [('name', '=ilike', city.strip())])
        if city_ids:
            city = city_obj.browse(cr, uid, city_ids[0], context)
            return city.phone_prefix
        else:
            return False

    def get_printable_tax(self, cr, uid, tax_line, context=None):
        if context is None:
            context = {}

        tax_obj = self.pool['account.tax']

        tax_id = tax_obj.get_tax_by_invoice_tax(cr, uid, tax_line.name, context=context)
        tax = tax_obj.browse(cr, uid, tax_id, context=context)
        if tax.tax_code_id.notprintable:
            return '', False
        else:
            tax_code = re.findall(r'[0-9]*', tax.description)[0]
            return tax_code, tax

    def get_tax_payability(self, cr, uid, invoice, context=None):
        payability = 'I'
        # import pdb; pdb.set_trace()
        for tax_line in invoice.tax_line:
            tax_id = self.pool['account.tax'].get_tax_by_invoice_tax(
                cr, uid, tax_line.name, context=context)
            tax = self.pool['account.tax'].browse(cr, uid, tax_id, context=context)
            if tax.payability != 'I':
                payability = tax.payability
        return payability

    def tax_creation(self, cr, uid, invoice, context=None):
        # created a separate function, so it is possible to extend on a separate module
        # create tax with max 8 taxes. Total length 248

        if not context:
            context = {}

        # This is required for correct tax search
        context['type'] = invoice.type

        tax_data = ''

        payability = self.get_tax_payability(cr, uid, invoice, context)
        no_tax = 0

        for count, tax_line in enumerate(invoice.tax_line, 1):
            tax_code, tax = self.get_printable_tax(cr, uid, tax_line, context)

            if tax:
                tax_values = {
                    'tax_code': tax_code,
                    'taxable': int(tax_line.base * 100),
                    'vat_code': int(tax_code),
                    'agro_vat_code': 0,
                    'vat11_code': 0,
                    'vat_total': int(tax_line.amount * 100),
                    # 'payability': tax.payability,
                    'law_reference': tax.law_reference,
                    'non_taxable_nature': tax.non_taxable_nature
                }
                tax_data += tax_template.format(**tax_values)
            else:
                no_tax += 1

        if not tax_data:
            raise orm.except_orm('Errore', 'Non ci sono tasse definite nella fattura {invoice}'.format(invoice=invoice.number))
        elif count > 8:
            raise orm.except_orm('Errore', 'Ci sono più di 8 tasse nella fattura {invoice}'.format(invoice=invoice.number))

        empty_tax_values = {
            'taxable': 0,
            'vat_code': 0,
            'agro_vat_code': 0,
            'vat11_code': 0,
            'vat_total': 0
        }

        for a in range(0, 8 - count + no_tax):
            tax_data += tax_template.format(**empty_tax_values)

        return tax_data, payability

    def account_creation(self, cr, uid, invoice, context=None):
        # Conti di ricavo/costo
        # La tabella costi/ricavi (lunghezza complessiva di 152 caratteri) è composta da 8 elementi
        account = {}
        account_data = ''
        for line in invoice.invoice_line:
            code = line.account_id.teamsystem_code or line.account_id.code

            if code in account:
                account[code] += line.price_subtotal
            else:
                account[code] = line.price_subtotal

        if not account:
            raise orm.except_orm('Errore', 'Non ci sono conti ricavo/costo definite nella fattura {invoice}'.format(invoice=invoice.number))
        elif len(account) > 8:
            raise orm.except_orm('Errore', 'Ci sono più di 8 conti ricavo/costo nella fattura {invoice}'.format(invoice=invoice.number))

        for account_code in account.keys():
            if isinstance(account_code, int):
                code = account_code
            else:
                code = account_code.isdigit() and int(account_code) or 5810501  # 5810501 è un numero fisso merci/vendita

            if len(str(code)) > 7:
                raise orm.except_orm(
                    'Errore',
                    'Il codice {} è troppo lungo. Fornire il codice specifico TeamSystem'.format(code))

            account_data += account_template.format(**{
                'account_proceeds': code,
                'total_proceeds': int(account.get(account_code) * 100)
            })

        for k in range(0, 8 - len(account)):
            account_data += account_template.format(**{
                'account_proceeds': 0,
                'total_proceeds': 0
            })

        return account_data

    def map_invoice_data(self, cr, uid, invoice_id, context):
        invoice = self.pool['account.invoice'].browse(cr, uid, invoice_id, context)

        if not invoice.number:
            raise orm.except_orm(_('Error'), u"Fattura al cliente {partner} {origine} non è stata emessa. ".format(
                partner=invoice.partner_id.name, origine=invoice.origin and u'con documento di origine {}'.format(invoice.origin) or ''))

        address_ids = self.pool['res.partner'].address_get(cr, uid, [invoice.partner_id.id], ['invoice', 'default'])
        address = self.pool['res.partner.address'].browse(cr, uid, address_ids['invoice'] or address_ids['default'], context)

        if invoice.partner_id.vat and address.country_id.code == 'IT':
            vat = invoice.partner_id.vat.isdigit() and invoice.partner_id.vat or re.findall('\d+', invoice.partner_id.vat)[0]
        else:
            vat = 0

        if invoice.type == 'out_invoice':
            causal = 1
        elif invoice.type == 'out_refund':
            causal = 2
        elif invoice.type == 'in_invoice':
            causal = 11
        elif invoice.type == 'in_refund':
            causal = 20
        else:
            raise orm.except_orm(_('Error'), _('Unknown Invoice Type'))

        prefix = self.get_phone_prefix(cr, uid, address.city, context)
        phone = get_phone_number(address.phone, prefix)
        fax = get_phone_number(address.fax, prefix)

        tax_data, payability = self.tax_creation(cr, uid, invoice, context)  # max 8

        # conti di ricavo/costo
        account_data = self.account_creation(cr, uid, invoice, context)

        if invoice.type == 'out_refund':
            vat_collectability = 3
        # elif tax_data[0].get('payability') == 'S':
        elif payability == 'S':
            vat_collectability = 4
        # elif tax_data[0].get('payability') == 'D':
        elif payability == 'D':
            vat_collectability = 1
        else:
            vat_collectability = 0
        if self.get_tax_payability(cr, uid, invoice, context) == 'S':
            vat_collectability = 4
                                        # 0=Immediata 1=Differita 2=Differita DL. 185/08
                                        # 3=Immediata per note credito/debito 4=Split payment
                                        # R=Risconto    C=Competenza
                                        # N=Non aggiorna estratto conto

        res = {
            'company_id': 1,
            'version': 3,
            'type': 0,
            'partner_id': 0,
            'name': invoice.partner_id.name.encode('latin', 'ignore')[:32],
            'address': address.street and address.street.encode('latin', 'ignore')[:30],
            'zip': address.zip and address.zip.isdigit() and int(address.zip and address.zip.replace('x', '0')[0:5] or '0') or 0,
            'city': address.city and address.city.encode('latin', 'ignore'),
            'province': address.province and address.province.code[:2],
            'fiscalcode': invoice.partner_id.fiscalcode or '',
            'vat_number': int(vat),
            'individual': invoice.partner_id.individual and 'S' or 'N',  # 134
            'space': 0,  # Posizione spazio fra cognome nome

            # Estero:
            'country': 0,  # Codice paese estero di residenza. Dove si prende il codice???
            'vat_ext': '',  # Solo 12 caratteri??? Doveva essere 14... Ex (Croazia): HR12345678901, Sweden: SE999999999901
            'fiscalcode_ext': '',

            # Dati di nascita,se questi dati sono vuoti vengono presi dal codice fiscale.
            'sex': '',  # M/F   173
            'birthday': 0,  # ggmmaaaa
            'city_of_birth': '',  # KGB?
            'province_of_birth': '',
            'phone_prefix': phone['prefix'],
            'phone': phone['number'][:20],
            'fax_prefix': fax['prefix'],
            'fax': fax['number'][:9],

            # Solo per i fornitori 246 -
            'account_code': 0,  # Codice conto di costo abituale (Solo per fornitori)
            'payment_conditions_code': invoice.payment_term and invoice.payment_term.teamsystem_code or 0,  # Codice condizioni di pagamento
            'abi': 0,  # ??
            'cab': 0,  # ??
            'partner_interm': 0,  # Codice intermedio clienti / fornitori  267

            # Dati fattura 268
            'causal': causal,    # Codice causale movimento
                            # Fattura di vendita=001
                            # Nota Credito = 002
                            # Fattura di acquisto=011
                            # Corrispettivo=020
                            # Movimenti diversi a diversi=027
                            # ( E' possibile indicare anche una causale multi collegata a una causale iva es. 101 collegata alla 1 )
                            # Vendita agenzia di viaggio=causale collegata alla 1 o alla 20 con il campo agenzia di viaggio = S
                            # Acquisti agenzia di viaggio=causale collagta alla 11 con il campo agenzia di viaggio = S
            'causal_description': self.causal_description[causal],  #
            'causal_ext': '',
            'causal_ext_1': '',
            'causal_ext_2': '',
            'registration_date': 0,  # Se 0 si intende uguale alla data documento
            'document_date': datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').strftime('%d%m%Y'),
            'document_number': invoice.supplier_invoice_number or 0,  # Numero documento fornitore compreso sezionale

            # TODO: Verifica TRF-NDOC e TRF-SERIE perché sono sbagliati
            'document_number_no_sectional': int(
                invoice.number.split('/')[invoice.journal_id.teamsystem_invoice_position]
            ),  # Numero documento (numero doc senza sezionale)
            'vat_sectional': invoice.journal_id.teamsystem_code,

            #  es. 1501 per una fattura numero 15 del sez. 1)
            # 'account_extract': int('{number:04}{section:02}'.format(number=int(invoice.number.split('/')[invoice.journal_id.teamsystem_invoice_position]), section=invoice.journal_id.teamsystem_code)),  # ??? Estratto conto Numero partita (numero doc + sezionale (tutto unito):
            #
            'account_extract': int(invoice.number.split('/')[invoice.journal_id.teamsystem_invoice_position]),  # Estratto conto Numero partita (numero doc):

            'account_extract_year': datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').year,  # Estratto conto Anno partita (anno di emissione della fattura in formato AAAA)
            'ae_currency': 0,  # Estratto conto in valuta Codice valuta estera
            'ae_exchange_rate': 0,  # 13(7+6 dec)
            'ae_date': 0,
            'ae_total_currency': 0,  # ??? 16(13+3dec) Estratto conto in valuta Totale documento in valuta
            'ae_total_currency_vat': 0,  # ??? 16(13+3dec) Estratto conto in valuta Totale iva in valuta
            # 'plafond_month': int(datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').strftime('%m%Y')),  # MMAAAA Riferimento PLAFOND e fatture diferite
            'plafond_month': 0,  # MMAAAA Riferimento PLAFOND e fatture diferite

            # Dati iva x8
            'tax_data': tax_data,

            # Totale fattura 723
            'invoice_total': int(
                round(self.pool['account.invoice'].get_total_fiscal(cr, uid, [invoice_id], context)[invoice_id] * 100, 0)
            ),  # Imponibile 6 dec?

            # Conti di ricavo/costo 735
            'account_data': account_data,

            # Dati eventuale pagamento fattura o movimenti diversi

            # Iva Editoria
            # pos. 6962:
            'vat_collectability': vat_collectability,
                                        # 0=Immediata 1=Differita 2=Differita DL. 185/08
                                        # 3=Immediata per note credito/debito 4=Split payment
                                        # R=Risconto    C=Competenza
                                        # N=Non aggiorna estratto conto

            'val_0': 0,
            'empty': '',
        }
        pprint(res)
        return res

    def maturity_creation(self, cr, uid, invoice, context=None):
        # Dettaglio effetti x 12 elementi

        maturity_data = ''
        count = 0

        for count, maturity_line in enumerate(invoice.maturity_ids, 1):
            maturity_values = {
                'payment_count': count,  # Numero rata
                'payment_deadline': int(datetime.datetime.strptime(maturity_line.date_maturity, '%Y-%m-%d').strftime('%d%m%Y')),  # Data scadenza
                'document_type': invoice.payment_term.riba and 2 or 3,      # Tipo effetto
                                                                            # 1=Tratta
                                                                            # 2=Ricevuta bancaria
                                                                            # 3=Rimessa diretta
                                                                            # 4=Cessioni
                                                                            # 5=Solo descrittivo
                                                                            # 6=Contanti alla consegna
                'payment_total': int(maturity_line.debit * 100 or maturity_line.credit * 100 or 0),  # Importo effetto
                'payment_total_currency': 0,  # Portafoglio in valuta. Importo effetto in valuta
                'total_stamps': 0,  # Importo bolli
                'payment_stamp_currency': 0,   # Portafoglio in valuta. Importo bolli  in valuta
                'payment_state': '0',  # Stato effetto 0=Aperto 1=Chiuso 2=Insoluto 3=Personalizzato
                'payment_subtype': '',  # Sottotipo rimessa diretta
            }
            maturity_data += maturity_template.format(**maturity_values)

        if count == 0:
            raise orm.except_orm('Errore', 'La fattura {invoice} non ha nessuna scadenza'.format(invoice=invoice.number))
        elif count > 12:
            raise orm.except_orm('Errore', 'Ci sono più di 12 scadenze nella fattura {invoice}'.format(invoice=invoice.number))

        empty_maturity_values = {
            'payment_count': 0,  # ??? Numero rata
            'payment_deadline': 0,  # ??? Data scadenza
            'document_type': 0,  # Tipo effetto
                                 # 1=Tratta
                                 # 2=Ricevuta bancaria
                                 # 3=Rimessa diretta
                                 # 4=Cessioni
                                 # 5=Solo descrittivo
                                 # 6=Contanti alla consegna
            'payment_total': 0,  # ??? Importo effetto
            'payment_total_currency': 0,  # Portafoglio in valuta. Importo effetto in valuta
            'total_stamps': 0,  # Importo bolli
            'payment_stamp_currency': 0,  # Portafoglio in valuta. Importo bolli  in valuta
            'payment_state': '0',  # Stato effetto 0=Aperto 1=Chiuso 2=Insoluto 3=Personalizzato
            'payment_subtype': '',  # Sottotipo rimessa diretta
        }

        for a in range(0, 12 - count):
            maturity_data += maturity_template.format(**empty_maturity_values)

        return maturity_data

    def map_deadline_data(self, cr, uid, invoice_id, context):
        invoice = self.pool['account.invoice'].browse(cr, uid, invoice_id, context)
        if invoice.payment_term and invoice.payment_term.teamsystem_code == 0:
            raise orm.except_orm('Errore', 'Impossibile da esportare la fattura numero {number} di {partner} in quanto sul termine di pagamento \'{payment}\' manca il codice TeamSystem'.format(number=invoice.number, partner=invoice.partner_id.name, payment=invoice.payment_term.name))

        maturity_data = self.maturity_creation(cr, uid, invoice, context)

        return {
            'company_id': 1,
            'version': 3,
            'type': 1,

            'val_0': 0,
            'empty': '',

            # Dati portafoglio
            'payment_condition': invoice.payment_term.teamsystem_code,  # Codice condizione di pagamento
            'abi': invoice.partner_id.bank_riba_id and int(invoice.partner_id.bank_riba_id.abi) or 0,  #
            'cab': invoice.partner_id.bank_riba_id and int(invoice.partner_id.bank_riba_id.cab) or 0,  #
            'agency_description': invoice.partner_id.bank_riba_id and invoice.partner_id.bank_riba_id.name.encode('latin', 'ignore')[:30],  # Descrizione agenzia
            'total_number_of_payments': len(invoice.maturity_ids),  # Numero totale rate
            'invoice_total': int(self.pool['account.invoice'].get_total_fiscal(cr, uid, [invoice_id], context)[invoice_id] * 100),  # Totale documento (totale fattura)

            'maturity_data': maturity_data,

            'agent_code': 0,  # Codice agente
            'paused_payment': '',  # Effetto sospeso
            'cig': '',
            'cup': '',

            # Movimenti INTRASTAT BENI dati aggiuntivi...
        }

    def get_accounting_data(self, cr, uid, invoice, context):
        account_data = ''
        account = {}

        empty_accounting = {
            'val_0': 0,
            'empty': '',
            'causal': 0,  # ??? Causale cont. industr.
                        # Fatt vendita = 001
                        # Fatt acquisto = 002
            'account': 0,   # ??? Conto cont. Industriale
                            # 1 = sistemi
                            # 2 = Noleggi
                            # 3 = domotica
            'account_proceeds': 0,   # ??? Voce di spesa / ricavo (uguale ai conti di ricavo contabilità generale ma con uno 0 in più)
                                            # 58100501
                                            # 58100502
                                            # 58100503
            'sign': '',  # ??? Segno ( D o A )
            'total_ammount': 0,  # Importo movimento o costo complessivo
            'quantity': 0
        }

        for line in invoice.invoice_line:
            if line.account_analytic_id:
                if line.account_analytic_id in account:
                    account[line.account_analytic_id] += line.price_subtotal
                else:
                    account[line.account_analytic_id] = line.price_subtotal

        if len(account) > 20:
            raise orm.except_orm('Errore', 'Ci sono più di 20 conti analitici nella fattura {invoice}'.format(invoice=invoice.number))

        accounting_data = ''

        for account_code in account.keys():
            code = account_code.code and account_code.code.isdigit() and int(account_code.code) or 5810501  # 5810501 è un numero fisso merci/vendita
            accounting_value = empty_accounting.copy()
            accounting_value.update({
                'account_proceeds': code,
                'total_ammount': int(account.get(account_code) * 100)
            })
            accounting_data += industrial_accounting_template.format(**accounting_value)

        for k in range(0, 20 - len(account)):
            accounting_data += industrial_accounting_template.format(**empty_accounting)

        return accounting_data

    def map_industrial_data(self, cr, uid, invoice_id, context):
        invoice = self.pool['account.invoice'].browse(cr, uid, invoice_id, context)
        return {
            'company_id': 1,
            'version': 3,
            'type': 2,

            'val_0': 0,
            # 'empty': '',

            # CONTAB. INDUSTRIALE 8
            'accounting_data': self.get_accounting_data(cr, uid, invoice, context)
        }

    def action_export_primanota(self, cr, uid, ids, context):
        file_name = 'TRAF2000{number}.txt'.format(number=ids and ids[0])
        file_data = StringIO()

        if context.get('active_ids'):
            invoice_ids = context['active_ids']
        else:
            return {'type': 'ir.actions.act_window_close'}

        for invoice_id in invoice_ids:
            invoice = self.pool['account.invoice'].browse(cr, uid, invoice_id, context)
            book_values = self.map_invoice_data(cr, uid, invoice_id, context)
            row = cash_book.format(**book_values)
            if not len(row) == 7001:
                raise orm.except_orm(_('Error'), "La lunghezza della riga Prima Nota errata ({}). Fattura {}".format(len(row), invoice.number))
            file_data.write(row)

            deadline_values = self.map_deadline_data(cr, uid, invoice_id, context)
            row = deadline_book.format(**deadline_values)
            if not len(row) == 7001:
                raise orm.except_orm(_('Error'), "La lunghezza della riga INTRASTAT errata ({}). Fattura {}".format(len(row), invoice.number))
            file_data.write(row)

            industrial_values = self.map_industrial_data(cr, uid, invoice_id, context)
            row = industrial_accounting.format(**industrial_values)
            if not len(row) == 7001:
                raise orm.except_orm(_('Error'), "La lunghezza della riga INDUSTRIALE errata ({}). Fattura {}".format(len(row), invoice.number))
            file_data.write(row)
            invoice.write({'teamsystem_export': True})
            text = invoice.number or invoice.name + _(' esportata in TeamSytem')
            self.pool['account.invoice'].log(cr, uid, invoice_id, text)
            self.pool['account.invoice'].message_append(cr, uid, [invoice_id], text, body_text=text, context=context)

        out = file_data.getvalue()
        out = out.encode("base64")
        return self.write(cr, uid, ids, {'state': 'end', 'data': out, 'name': file_name}, context=context)
