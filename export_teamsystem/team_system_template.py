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

cash_book = """{company_id:05}{version:1}{type:1}\
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
{plafond_month:06}"""

# Dati Iva 475
tax_template = "{taxable:012}{vat_code:03}{agro_vat_code:03}{vat11_code:02}{vat_total:011}"

cash_book += "{tax_data}"

# Totale fattura
cash_book += "{invoice_total:012}"

# Conti di ricavo/costo 735
account_template = "{account_proceeds:07}{total_proceeds:012}"
cash_book += "{account_data}"

# Dati eventuale pagamento fattura o movimenti diversi 887
cash_book += "{val_0:03}{empty:15}{empty:34}{empty:34}"

# # a tabella altri movimenti (lunghezza complessiva di 5120 caratteri)
# # è composta da 80 elementi i che comprendono i campi da TRF-CONTO a TRF-EC-IMP-VAL
cash_book += "{val_0:07} {val_0:012}{empty:18}{val_0:06}{val_0:04}{val_0:016}" * 80

# Ratei e risconti 6093
# La tabella ratei e risconti (lunghezza complessiva di 190 caratteri)
# è composta da 10 elementi i che comprendono i campi da TRF-RIFER-TAB a TRF-DT-FIN
cash_book += "{empty:1}{val_0:02}{val_0:08}{val_0:08}" * 10

# N.doc. a 6 cifre se non bastano le 5 di TRF-NDOC (That's why this format should be banned)
cash_book += "{val_0:06}"

# Ulteriori dati cliente fornitore
cash_book += "{empty:1}{val_0:01}"

# # Ulteriori dati eventuale pagamento fattura o movimenti diversi 6291
cash_book += "{val_0:02}" * 80

# Ulteriori dati gestione professionista per eventuale pagamento incasso fattura o dati fattura
cash_book += "{val_0:07}{val_0:08}{val_0:012}{val_0:012}{val_0:012}{val_0:012}{val_0:012}{val_0:012}"

# Ulteriori dati per unità produttive  ricavi 6538
cash_book += "{val_0:02}" * 8

# Ulteriori dati per unita’ produttive pagamenti
cash_book += "{val_0:02}" * 80

# Ulteriori dati cliente fornitore
cash_book += "{empty:4}{empty:20}{empty:1}{empty:1}"

# Ulteriori dati gestione professionista per eventuale incasso/ pagamento fattura o dati fattura 6740
cash_book += "{val_0:07}{val_0:07}{val_0:07}{val_0:07}{val_0:07}{val_0:07}"

# Varie 6782
cash_book += "{empty:1}{empty:1}{val_0:08}{val_0:03}"

# Prima nota previsionale dati aggiuntivi 6795
cash_book += "{empty:1}{empty:1}{val_0:08}{val_0:08}{empty:1}"

# Varie 6814
cash_book += """{empty:20}{val_0:02}{val_0:01}{val_0:07}{val_0:011}{empty:12}{empty:32}{val_0:08}\
{empty:1}{val_0:06}{empty:1}{val_0:02}{empty:1}"""

# Iva Editoria 6918
cash_book += "{val_0:03}" * 8
cash_book += """{empty:1}{empty:16}{empty:1}{empty:1}{empty:1}{vat_collectability:01}\
{empty:1}{empty:1}{empty:1}{empty:1}{val_0:06}{empty:20}\
{empty:1}{empty:1}{empty:1}{empty:1}{empty:1}{empty:1}{empty:1}"""

# ODOA CRLF
cash_book += "\r\n"


# portafoglio/scadenze
deadline_book = """{company_id:05}{version:1}{type:1}\
{val_0:05}{val_0:02}{val_0:03}{val_0:014}"""

# Movimenti INTRASTAT BENI
deadline_book += """{empty:8}{val_0:012}{val_0:012}{empty:1}{val_0:012}{val_0:012}{val_0:012}\
{empty:1}{empty:1}{val_0:03}{val_0:03}{val_0:03}{empty:2}{empty:2}{empty:1}""" * 20
deadline_book += "{empty:1}{val_0:06}{empty:173}"

# Ritenuta d’acconto 1912
deadline_book += """{val_0:01}{val_0:011}{val_0:04}{val_0:010}{val_0:011}{val_0:06}{val_0:02}{val_0:04}{val_0:08}\
{val_0:011}{val_0:01}{empty:4}{empty:12}{empty:12}{val_0:05}{val_0:05}{val_0:04}{val_0:11}"""

# Dati contributo INPS e modello GLA/D 2034
deadline_book += """{empty:1}{val_0:011}{val_0:011}{val_0:011}{val_0:011}{empty:11}{val_0:08}{val_0:011}{val_0:011}\
{val_0:08}{val_0:08}{val_0:02}{val_0:02}{val_0:03}{val_0:011}{empty:184}"""

# Dati portafoglio
deadline_book += """{payment_condition:03}{abi:05}{cab:05}{agency_description:30}{total_number_of_payments:02}{invoice_total:012}"""

# Dettaglio effetti 2395

maturity_template = """{payment_count:02}{payment_deadline:08}{document_type:01}\
{payment_total:012}{payment_total_currency:015}{total_stamps:012}{payment_stamp_currency:015}\
{payment_state:1}{payment_subtype:1}"""

deadline_book += "{maturity_data}"

deadline_book += "{agent_code:04}"
deadline_book += "{paused_payment:1}" * 12
deadline_book += "{cig:15}{cup:15}{empty:294}"

# Movimenti INTRASTAT BENI dati aggiuntivi 3539
deadline_book += "{empty:3}{empty:16}" * 20

# Movimenti INTRASTAT SERVIZI 3919
deadline_book += """{empty:6}{val_0:03}{val_0:012}{val_0:012}{val_0:08}{empty:1}{empty:1}\
{val_0:06}{val_0:06}{val_0:06}{val_0:02}{empty:15}{empty:1}{empty:3}{empty:16}""" * 20
deadline_book += "{empty:1}{val_0:06}"

# Check iva reverse charge 5886
deadline_book += "{empty:1}" * 8
deadline_book += "{empty:15}{empty:1091}"

# ODOA CRLF
deadline_book += "\r\n"

# CONTABILITA’ INDUSTRIALE
industrial_accounting = u"{company_id:05}{version:1}{type:1}"

# CONTAB. INDUSTRIALE 8
industrial_accounting_template = """{causal:03}{account:08}{account_proceeds:08}{val_0:08}{val_0:08}{val_0:06}\
{val_0:03}{empty:20}{sign:1}{quantity:012}{val_0:017}{total_ammount:018}{val_0:012}{val_0:010}{val_0:017}{val_0:017}\
{empty:18}{val_0:03}{val_0:03}{val_0:06}{val_0:03}{val_0:01}"""
industrial_accounting += "{accounting_data}"

# 4048
industrial_accounting += "{val_0:02}" * 20

industrial_accounting += "{val_0:02912}"

# ODOA CRLF
industrial_accounting += "\r\n"
