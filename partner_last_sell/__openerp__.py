# -*- encoding: utf-8 -*-
# © 2018 Didotech srl (www.didotech.com)
#

{
    'name': 'Partner Last Sale',
    'version': '3.0.1.0',
    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'depends': [
        'partner_blacklist',
    ],
    'category': 'Generic Modules',
    'description': '''
Adds the last sale date of a customer
''',
    'data': [
        'views/partner_view.xml',
    ],
    'active': False,
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
