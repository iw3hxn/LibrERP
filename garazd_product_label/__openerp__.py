# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 Yurii Razumovskyi <support@garazd.biz>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Custom Product Labels',
    'version': '10.0.1.0.3',
    'category': 'Product Management',
    'author': 'Garazd Creation',
    'website': "https://garazd.biz",
    'license': 'LGPL-3',
    'summary': """Print custom product labels""",
    'images': ['static/description/banner.png'],
    'description': """
Module allows to print custom product labels on different paper formats.
Label size: 60x35mm, paperformat: 
    - A4 (24 pcs per sheet, 3 pcs x 8 rows).
    """,
    'depends': ['product'],
    'data': [
        'wizard/print_product_label_views.xml',
        'report/product_report.xml'
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
