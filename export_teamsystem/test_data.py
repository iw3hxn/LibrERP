# -*- coding: utf-8 -*-
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

from team_system_template import cash_book, account_template, tax_template
from team_system_template import deadline_book, industrial_accounting_template, industrial_accounting

tax_data = tax_template.format(**{
    'taxable': 240000000,  # Imponibile 6 dec?
    'vat_code': 22,  # Aliquota Iva o Codice esenzione
    'agro_vat_code': 0,  # Aliquota iva di compensazione agricola
    'vat11_code': 0,
    'vat_total': 52800}
) * 8

account_data = account_template.format(**{
    'account_proceeds': 5810502,
    'total_proceeds': 240000000  # Imponibile 6 dec?
}) * 8


cash_book_values = {
    'company_id': 1,
    'version': 3,
    'type': 0,
    'partner_id': 34,
    'name': 'Cliente prova con nome estremamente lungo'[:32],
    'address': 'via Tre Porcellini'[:30],
    'zip': 35020,
    'city': 'Padova',
    'province': 'PD'[:2],
    'fiscalcode': 'RSSMRA85T10A562S',
    'vat_number': 01032450072,
    'individual': True and 'S' or 'N',  # 134
    'space': 0,  # Posizione spazio fra cognome nome

    # Estero:
    'country': 0,  # Codice paese estero di residenza. Dove si prende il codice???
    'vat_ext': '',  # Solo 12 caratteri??? Doveva essere 14... Ex (Croazia): HR12345678901, Sweden: SE999999999901
    'fiscalcode_ext': '',

    # Dati di nascita,se questi dati sono vuoti vengono presi dal codice fiscale.
    'sex': 'M',  # M/F   173
    'birthday': 01012001,  # ggmmaaaa
    'city_of_birth': 'Palermo',  # KGB?
    'province_of_birth': 'PA',
    'phone_prefix': '091',
    'phone': '1234567',
    'fax_prefix': '0921',
    'fax': '7890123',

    # Solo per i fornitori 246 -
    'account_code': 9999999,  # Codice conto di costo abituale
    'payment_conditions_code': 4444,  # Codice condizioni di pagamento
    'abi': 3002,
    'cab': 3280,
    'partner_interm': 2,  # Codice intermedio clienti / fornitori  267

    # Dati fattura 268
    'causal': 1,    # Codice causale movimento
                    # Fattura di vendita=001
                    # Nota Credito = 002
                    # Fattura di acquisto=011
                    # Corrispettivo=020
                    # Movimenti diversi a diversi=027
                    # ( E' possibile indicare anche una causale multi collegata a una causale iva es. 101 collegata alla 1 )
                    # Vendita agenzia di viaggio=causale collegata alla 1 o alla 20 con il campo agenzia di viaggio = S
                    # Acquisti agenzia di viaggio=causale collagta alla 11 con il campo agenzia di viaggio = S
    'causal_description': 'FATT. VENDITA',
    'causal_ext': 'Causale aggiuntiva',
    'causal_ext_1': 'Causale aggiuntiva 1',
    'causal_ext_2': 'Causale aggiuntiva 2',
    'registration_date': 0,  # Se 0 si intende uguale alla data documento
    'document_date': 01012016,
    'document_number': 345,  # Numero documento fornitore compreso sezionale
    'document_number_no_sectional': 34,  # Numero documento (numero doc senza sezionale)
    'vat_sectional': 22,
    'account_extract': 1501,  # Estratto conto Numero partita (numero doc + sezionale (tutto unito):
                              #  es. 1501 per una fattura numero 15 del sez. 1)
    'account_extract_year': 2016,  # Estratto conto Anno partita (anno di emissione della fattura in formato AAAA)
    'ae_currency': 0,  # Estratto conto in valuta Codice valuta estera
    'ae_exchange_rate': 1000000,  # 13(7+6 dec)
    'ae_date': 23012016,
    'ae_total_currency': 240000,  # 16(13+3dec)
    'ae_total_currency_vat': 52800,  # 16(13+3dec)
    'plafond_month': 012016,  # MMAAAA Riferimento PLAFOND e fatture diferite

    # Dati iva
    'tax_data': tax_data,

    # Totale fattura
    'invoice_total': 240000000,  # Imponibile 6 dec?

    # Conti di ricavo/costo
    'account_data': account_data,

    # Dati eventuale pagamento fattura o movimenti diversi

    # Iva Editoria
    'vat_collectability': 0,    # 0=Immediata 1=Differita 2=Differita DL. 185/08
                                # 3=Immediata per note credito/debito 4=Split payment
                                # R=Risconto    C=Competenza
                                # N=Non aggiorna estratto conto

    'val_0': 0,
    'empty': ''
}

deadline_book_values = {
    'company_id': 1,
    'version': 3,
    'type': 1,

    # Dati INTRASTAT

    'val_0': 0,
    'empty': '',

    # Dati portafoglio
    'payment_condition': 0,  # ??? Codice condizione di pagamento
    'abi': 0,  # ???
    'cab': 0,  # ???
    'agency_description': '',  # Descrizione agenzia
    'total_number_of_payments': 0,  # ??? Numero totale rate
    'invoice_total': 0, # ??? Totale documento (totale fattura)

    # Dettaglio effetti
    'payment_count': 0,  # ??? Numero rata
    'payment_deadline': 0,  # ??? Data scadenza
    'document_type': 0,     # Tipo effetto
                            # 1=Tratta
                            # 2=Ricevuta bancaria
                            # 3=Rimessa diretta
                            # 4=Cessioni
                            # 5=Solo descrittivo
                            # 6=Contanti alla consegna
    'payment_total': 0,  # ??? Importo effetto
    'payment_total_currency': 0,  # Portafoglio in valuta. Importo effetto in valuta
    'total_stamps': 0,  # Importo bolli
    'payment_stamp_currency': 0,   # Portafoglio in valuta. Importo bolli  in valuta
    'payment_state': '',  # ??? Stato effetto 0=Aperto 1=Chiuso 2=Insoluto 3=Personalizzato
    'payment_subtype': '',  # Sottotipo rimessa diretta
    'agent_code': 0,  # Codice agente
    'paused_payment': '',  # Effetto sospeso
    'cig': '',
    'cup': '',

    # Movimenti INTRASTAT BENI dati aggiuntivi...
}


def get_accounting_data():
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
    }

    accounting_data = ''

    for k in range(0, 20):
        accounting_data += industrial_accounting_template.format(**empty_accounting)

    return accounting_data


industrial_accounting_values = {
    'company_id': 1,
    'version': 3,
    'type': 2,

    'val_0': 0,
    # 'empty': '',

    # CONTAB. INDUSTRIALE 8
    'accounting_data': get_accounting_data()
}

if __name__ == '__main__':
    record_type = 0

    if record_type == 0:
        record = cash_book.format(**cash_book_values)
    elif record_type == 1:
        record = deadline_book.format(**deadline_book_values)
    elif record_type == 2:
        record = industrial_accounting.format(**industrial_accounting_values)

    print record

    # for s in record:
    #     print 'X:', s

    print len(record)
