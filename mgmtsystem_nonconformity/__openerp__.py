# -*- encoding: utf-8 -*-

{
    "name": "Management System - Nonconformity",
    "version": "1.0d",
    "author": "Savoir-faire Linux,Odoo Community Association (OCA) - refactoring by Antonio Mignolli - Didotech SRL",
    "website": "http://www.savoirfairelinux.com",
    "license": "AGPL-3",
    "category": "Management System",
    "description": """\
This module enables you to manage the nonconformities of your management 
system : quality (ISO9001), environment (ISO14001) or security (ISO27001).	

WARNING: when upgrading from v0.1, data conversion is required, since there are subtancial changes to the data structure.
    """,
    "depends": [
        'mgmtsystem_action',
        'wiki_procedure',
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/mgmtsystem_nonconformity_security.xml',
        'views/mgmtsystem_nonconformity.xml',
        'views/mgmtsystem_nonconformity_workflow.xml',
        'views/nonconformity_sequence.xml',
        'views/board_mgmtsystem_nonconformity.xml',
        'views/view_partner_form.xml',
        'views/mgmtsystem_nonconformity_location.xml',
#        'mgmtsystem_nonconformity_data.xml',
    ],
    "demo": [
        'demo_nonconformity.xml',
    ],
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

