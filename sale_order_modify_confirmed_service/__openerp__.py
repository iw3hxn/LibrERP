# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

{
    'name': "Wizard Modifica Ordini Service",
    'version': '3.0.2.4',
    'category': 'Sales Management',
    'description': """Wizard per la modifica di sale order consegnati,
    solo per i prodotti di tipo service.
Il modulo prevede la modifica di indirizzi e informazioni sulle righe
come prezzo e sconto.
Basato su sale_order_modify_confirmed""",
    'author': 'Antonio Mignolli - Didotech Srl',
    'website': 'www.didotech.com',
    'license': 'AGPL-3',
    "depends": ['sale', 'sale_margin'],
    "update_xml": [
        'security/ir.model.access.csv',
        'wizard/wizard_modify_order.xml',
        'views/sale_view.xml'
    ],
    "active": False,
    "installable": True
}
