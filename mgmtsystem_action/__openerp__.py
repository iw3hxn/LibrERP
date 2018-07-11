# -*- encoding: utf-8 -*-

{
    "name": "Management System - Action",
    "version": "1.1.a",
    "author": "Savoir-faire Linux,Odoo Community Association (OCA) - refactored by Antonio Mignolli - Didotech SRL",
    "website": "http://www.savoirfairelinux.com",
    "license": "AGPL-3",
    "category": "Management System",
    "description": """\
This module enables you to manage the different actions of your management system :
  * immediate actions
  * corrective actions
  * preventive actions
  * improvement opportunities.

WARNING: when upgrading from v0.1, data conversion is required, since there are subtancial changes to the data structure.
    """,
    "depends": [
        'mgmtsystem',
        'audittrail',
        'crm_claim'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/mgmtsystem_action.xml',
        'views/action_sequence.xml',
        'views/board_mgmtsystem_action.xml',
        'views/workflow_mgmtsystem_action.xml',
    ],
    "demo": ['demo_action.xml'],
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

