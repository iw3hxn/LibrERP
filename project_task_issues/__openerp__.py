# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2014 Matmoz d.o.o. (<http://www.matmoz.si>)
#    Copyright (C) 2020 Didotech srl (<http://www.didotech.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU AfferoGeneral Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Project Task Issues',
    'version': '3.3.5.9',
    'category': 'Generic Modules/Projects & Services',
    'description': """Issues list associated to task. In the task form, you can see the issues related to that task
		Create issues from tasks.""",
    'author': 'Agile Business Group, Didotech SRL',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": [
        'project_issue_sheet'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/project_issue_menu.xml',
        'views/project_view.xml',
        'views/project_issue_view.xml',
        'views/project_issue_status_view.xml'
    ],
    "active": False,
    "installable": True
}
