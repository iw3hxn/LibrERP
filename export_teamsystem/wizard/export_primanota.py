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

from openerp.addons.export_teamsystem.team_system_template import cash_book


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

import pdb


def get_phone_number(number, prefix=''):
    phone = ''
    if number:
        if number[0] == '+':
            raise orm.except_orm(_('Warning'), _("Phone numbers beginning with '+' are not handled yet"))
        else:
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

    def map_invoice_data(self, cr, uid, invoice_id, context):
        invoice = self.pool['account.invoice'].browse(cr, uid, invoice_id, context)

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



        return {
            'company_id': 1,
            'version': 3,
            'type': 0,
            'partner_id': 0,
            'name': invoice.partner_id.name[:32],
            'address': address.street and address.street[:30],
            'zip': int(address.zip),
            'city': address.city,
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
            'phone': phone['number'],
            'fax_prefix': fax['prefix'],
            'fax': fax['number'],

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
            'document_number_no_sectional': int(invoice.number.split('/')[invoice.journal_id.teamsystem_invoice_position]),  # ??? Numero documento (numero doc senza sezionale)
            'vat_sectional': invoice.journal_id.teamsystem_code,  # ???
            'account_extract': int('{number:04}{section:02}'.format(number=int(invoice.number.split('/')[invoice.journal_id.teamsystem_invoice_position]), section=invoice.journal_id.teamsystem_code)),  # ??? Estratto conto Numero partita (numero doc + sezionale (tutto unito):
                #  es. 1501 per una fattura numero 15 del sez. 1)
            'account_extract_year': datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').year,  # Estratto conto Anno partita (anno di emissione della fattura in formato AAAA)
            'ae_currency': 0,  # Estratto conto in valuta Codice valuta estera
            'ae_exchange_rate': 0,  # 13(7+6 dec)
            'ae_date': 0,
            'ae_total_currency': 0,  # ??? 16(13+3dec) Estratto conto in valuta Totale documento in valuta
            'ae_total_currency_vat': 0,  # ??? 16(13+3dec) Estratto conto in valuta Totale iva in valuta
            # 'plafond_month': int(datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').strftime('%m%Y')),  # MMAAAA Riferimento PLAFOND e fatture diferite
            'plafond_month': 0,  # MMAAAA Riferimento PLAFOND e fatture diferite

            # Dati iva
            'taxable': int(invoice.amount_untaxed * 1000000),  # Imponibile 6 dec?
            'vat_code': 22,  # ??? Aliquota Iva o Codice esenzione
            'agro_vat_code': 0,  # Aliquota iva di compensazione agricola
            'vat11_code': 0,
            'vat_total': int(invoice.amount_tax * 1000000),

            # Unknown
            'val_1': 0,
            'val_2': 0,
            'val_3': 0,
            'val_4': 0,
            'val_5': 0,
            'val_6': 0,
            'val_7': 0,

            # Totale fattura
            'invoice_total': int(invoice.amount_total * 1000000),  # Imponibile 6 dec?

            # Conti di ricavo/costo 735
            'account_proceeds': 5810502,  # ??? Codice conto di ricavo/costo
            'total_proceeds': 0,  # ?? Imponibile 6 dec?

            # Dati eventuale pagamento fattura o movimenti diversi

                # Iva Editoria
            'vat_collectability': 0,    # 0=Immediata 1=Differita 2=Differita DL. 185/08
                                        # 3=Immediata per note credito/debito 4=Split payment
                                        # R=Risconto    C=Competenza
                                        # N=Non aggiorna estratto conto

            'val_0': 0,
            'empty': '',

        }

    def map_deadline_data(self, cr, uid, invoice_id, context):

        return {
            'val_0': 0,
            'empty': ''
        }

    def action_export_primanota(self, cr, uid, ids, context):
        file_name = 'Primanota.txt'
        file_data = StringIO()

        if context.get('active_ids'):
            invoice_ids = context['active_ids']
        else:
            return {'type': 'ir.actions.act_window_close'}

        for invoice_id in invoice_ids:
            book_values = self.map_invoice_data(cr, uid, invoice_id, context)
            file_data.write(cash_book.format(**book_values))

        out = file_data.getvalue()
        out = out.encode("base64")
        return self.write(cr, uid, ids, {'state': 'end', 'data': out, 'name': file_name}, context=context)
