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

cash_book = u"""{company_id:05}{version:1}{type:1}\
{partner_id:05}{name:32}{address:30}{zip:05}{city:25}{province:2}\
{fiscalcode:16}{vat_number:011}{individual:1}{space:02}\
{country:04}{vat_ext:12}{fiscalcode_ext:20}\
{sex:1}{birthday:8}{city_of_birth:25}{province_of_birth:2}\
{phone_prefix:4}{phone:20}{fax_prefix:4}{fax:9}\
{account_code:07}{payment_conditions_code:04}{abi:05}{cab:05}\
{partner_interm:1}{causal:03}{causal_description:15}{causal_ext:18}{causal_ext_1:34}{causal_ext_2:34}\
{registration_date:8}{document_date:8}{document_number:08}{document_number_no_sectional:05}\
{vat_sectional:02}{account_extract:06}{account_extract_year:04}\
{ae_currency:03}{ae_exchange_rate:013}{ae_date:08}{ae_total_currency:016}{ae_total_currency_vat:016}\
{plafond_month:06}\
{taxable:012}{vat_code:03}{agro_vat_code:03}{vat11_code:02}{vat_total:012} \
{val_1:030} {val_2:030} {val_3:030} {val_4:030} {val_5:030} {val_6:030} {val_7:030}\
{invoice_total:012}\
{account_proceeds:07}{total_proceeds:012}\
{val_0:06} {val_0:018} {val_0:018} {val_0:018} {val_0:018} {val_0:018} {val_0:018} {val_0:014}\
{empty:83}"""

# a tabella altri movimenti (lunghezza complessiva di 5120 caratteri)
# è composta da 80 elementi i che comprendono i campi da TRF-CONTO a TRF-EC-IMP-VAL
cash_book += "{val_0:07} {val_0:012}{empty:18}{val_0:06}{val_0:04}{val_0:016}" * 80

# Ratei e risconti
# La tabella ratei e risconti (lunghezza complessiva di 190 caratteri)
# è composta da 10 elementi i che comprendono i campi da TRF-RIFER-TAB a TRF-DT-FIN
cash_book += "{empty:1}{val_0:02}{val_0:08}{val_0:08}" * 10

# N.doc. a 6 cifre se non bastano le 5 di TRF-NDOC (That's why this format should be banned)
cash_book += "{val_0:06}"

# Ulteriori dati cliente fornitore
cash_book += "{empty:1}{val_0:01}"

# Ulteriori dati eventuale pagamento fattura o movimenti diversi
cash_book += "{val_0:02}" * 80

# Ulteriori dati gestione professionista per eventuale pagamento incasso fattura o dati fattura
cash_book += "{val_0:07}{val_0:08}{val_0:012}{val_0:012}{val_0:012}{val_0:012}{val_0:012}{val_0:012}"

# Ulteriori dati per unità produttive  ricavi
cash_book += "{val_0:02}" * 8

# Ulteriori dati per unita’ produttive pagamenti
cash_book += "{val_0:02}" * 80

# Ulteriori dati cliente fornitore
cash_book += "{empty:4}{empty:20}{empty:1}{empty:1}"

# Ulteriori dati gestione professionista per eventuale incasso/ pagamento fattura o dati fattura
cash_book += "{val_0:07}{val_0:07}{val_0:07}{val_0:07}{val_0:07}{val_0:07}"

# Varie
cash_book += "{empty:1}{empty:1}{val_0:08}{val_0:03}"

# Prima nota previsionale dati aggiuntivi
cash_book += "{empty:1}{empty:1}{val_0:08}{val_0:08}{empty:1}"

# Varie 6814
cash_book += """{empty:20}{val_0:02}{val_0:01}{val_0:07}{val_0:011}{empty:12}{empty:32}{val_0:08}\
{empty:1}{val_0:06}{empty:1}{val_0:02}{empty:1}"""

# Iva Editoria
cash_book += "{val_0:03}" * 8
cash_book += """{empty:1}{empty:16}{empty:1}{empty:1}{empty:1}{vat_collectability:01}\
{empty:1}{empty:1}{empty:1}{empty:1}{val_0:06}{empty:20}\
{empty:1}{empty:1}{empty:1}{empty:1}{empty:1}{empty:1}{empty:1}"""

# ODOA CRLF
cash_book += "\r\n"
