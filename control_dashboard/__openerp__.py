# -*- coding: utf-8 -*-
##############################################################################
#
#    by Bortolatto Ivan (ivan.bortolatto at didotech.com)
#    Copyright (C) 2013 Didotech Inc. (<http://www.didotech.com>)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


{
    "name": "Virtual Desk for Alert",
    "version": "1.3.7",
    "depends": ["base", "mail", "base_calendar", "email_template"],
    'complexity': "easy",
    'description': """
This is a full-featured calendar system.
========================================

It supports for Appointment:
    - Calendar of events
    - Alerts (create requests)
    - Recurring events
    - Invitations to people

If you need to manage your meetings, you should install the CRM module.
    """,
    "author": "Didotech inc.",
    'category': 'Tools',
    'website': 'http://www.didotech.com',
    "init_xml": [
    ],
    'images': [],
    "demo_xml": [],
    "update_xml": [
        "ir_alert_view.xml",
        "ir_alert_workflow.xml",
        "board_alert_view.xml",
        "data/alert_config_data.xml",
        "security/ir.model.access.csv",
    ],
    "test": [],
    "installable": True,
    "auto_install": False,
    "images": [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
