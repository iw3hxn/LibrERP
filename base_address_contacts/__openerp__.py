# -*- coding: utf-8 -*-
# © 2013 - TODAY Denero Team. (www.deneroteam.com>)
# © 2017 Didotech srl (www.didotech.com)

{
    'name': 'Base Address Contact',
    'version': '3.3.13.11',
    'category': 'Base',
    'description': """
This module allows you to manage your contacts
==============================================

!!!IMPORTANT - this module conflicts with the base_contact module.

It lets you define:
    * several contacts related to a partner address instead of partner_id,

    use context['import'] = True 


""",
    'author': 'Denero Team',
    'website': 'http://www.deneroteam.com',
    'depends': ['base'],
    'update_xml': [
        'views/res_partner_address_view.xml',
        'security/ir.model.access.csv'
    ],
    'conflicts': [
        'base_contact',
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
