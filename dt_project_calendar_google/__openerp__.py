# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2013-2014 Didotech srl (<http://www.didotech.com>). All Rights Reserved
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Google sync Project Task",
    "version": "3.1.2.1",
    "author": "Tiny/ Repinfo/ Didotech SRL",
    "website": "http://www.didotech.com",
    "category": "Generic Modules",
    "description": """
        Synchro Export/Import shared calendar to google calendar
    """,
    "depends": [
        "crm",
        "project_calendar",
        "google_base_account"
    ],
    "data": [
        'google_meeting_view.xml',
#        'google_meeting_wizard.xml',
        'google_meeting_cron.xml'
    ],
    "active": False,
    "installable": True,
}
