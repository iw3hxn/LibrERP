# -*- coding: utf-8 -*-
# © 2018-2020 Didotech srl (www.didotech.com)

{ 
    'name': 'Aeroo Reports - LibreOffice Helper Addon',
    'version': '4.0.2.0',
    'category': 'Generic Modules/Aeroo Reporting',
    'description': """
Aeroo Reports LibreOffice.org helper adds following features:

* Additional output formats for ODF reports;
* ODF subreport feature;
* Include external ODF documents feature;
* Process each object separately or in group;

Supported output format combinations (Template -> Output):
=================================================================
odt -> pdf
odt -> doc
ods -> pdf
ods -> xls
ods -> csv
""",
    'author': 'Andrei Levin - Didotech Srl',
    'website': 'www.didotech.com',
    'category': 'Generic Modules/Aeroo Reporting',
    'depends': [
        'base',
        'report_aeroo'
    ],
    'data': [
        "installer.xml",
        "report_view.xml",
        "data/report_aeroo_data.xml"
    ],
    'installable': True,
    'active': False
}
