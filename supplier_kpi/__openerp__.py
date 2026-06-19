# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2025 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Supplier KPI (ISO 9001)',
    'version': '1.1',
    'author': 'Didotech SRL',
    'category': 'Reporting',
    'description': """
KPI Fornitori per ISO 9001
==========================

Ritardi ricezione per riga d'ordine (ddt_in_date vs date_planned)
e conteggio non conformità da giornali di magazzino flaggati.

Funzionalità:
- Report ritardi consegna fornitori: calcola i giorni di ritardo/anticipo
  per ogni entrata merce rispetto alla data pianificata sulla riga PO.
- Report non conformità fornitori: conta i picking associati a giornali
  di magazzino marcati come non conformità, con filtro opzionale sulle
  note (keyword RMA/Reso).
- Inizializzazione automatica dei flag di non conformità sui giornali
  standard di reso/riparazione.
    """,
    'depends': [
        'stock',
        'purchase',
        'l10n_it_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/stock_journal_data.xml',
        'views/inherit_res_partner.xml',
        'views/supplier_kpi_report.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
