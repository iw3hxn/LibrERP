# -*- encoding: utf-8 -*-
##############################################################################
#

{
    'name': 'Partner Incoterms',
    'version': '3.0.0.0',
    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'purchase',
        'sale',
        'delivery'
    ],
    'category': 'Generic Modules',
    'description': '''
Adds a default purchase Incoterm to the partner object which will be copied onto the Purchase Order incoterm as default
''',
    'data': [
        'views/partner_view.xml',
        'views/purchase_view.xml',
    ],
    'active': False,
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
