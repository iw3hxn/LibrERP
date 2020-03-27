# -*- encoding: utf-8 -*-
##############################################################################
#
#    Parthiv Pate, Tech Receptives, Open Source For Ideas    
#    Copyright (C) 2009-Today Tech Receptives(http://techreceptives.com).
#    All Rights Reserved
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Letter Management",
    "version": "3.4.2.9",
    "depends": [
        "base"
    ],
    "author": "Parthiv Patel, Tech Receptives, Didotech SRL",
    "category": "Generic",
    "description": """
        Using this module you can track Incoming / Outgoing letters, parcels, registered documents
        or any other paper documents that are important for company to keep track of.
    """,
    "init_xml": [],
    'depends': [
        'hr',
        'base_address_contacts',
        'web_wysiwyg',
        'web_display_html'
    ],
    'update_xml': [
        "security/letter_security.xml",
        "security/ir.model.access.csv",
        "views/letter_mgmt_config_view.xml",
        "views/letter_mgmt_view.xml",
        "letter_sequence.xml",
        "letter_demo.xml",
        # 'wizard/add_letter_type.xml'
    ],
    # 'demo_xml': ["letter_demo.xml"],
    'installable': True,
    'active': False,
    # 'certificate': 'certificate',
}
