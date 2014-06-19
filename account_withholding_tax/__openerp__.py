# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>)
#    Copyright (C) 2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': "Management of withholding tax",
    'version': '3.0.0.1',
    'category': 'Accounting & Finance',
    'description': """
Withholding tax on purchase invoices
==========================================

To use the module you need to configure the fields associated with the company:
  - Journal that will contain records related to the withholding tax
and those in the configuration of the tax:
  - Payment term for payment of withholding
  - Boolean to handle the withholding tax
""",
    'author': 'Didotech srl',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends" : ['account_voucher',],
    "data" : [
        'account_view.xml',
        'tax_view.xml',
        ],
    "demo" : [],
    "active": False,
    "installable": True
}
