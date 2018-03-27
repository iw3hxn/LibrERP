# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Didotech.com (info at didotech.com)
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
    'name': 'Human Resources/Sim Card Asset',
    'version': '3.0.7.1',
    'category': 'Generic Modules/Human Resources',
    'description': """A generic module to manage the employee and mobile asset""",
    "author": "Denero Team @ Didotech.com",
    'depends': [
        'hr',
        'report_aeroo',
        'web_hide_buttons'
    ],
    'init_xml': [
        'security/sim_security.xml',
        'security/ir.model.access.csv',
        'res_sim_view.xml'
    ],
    'update_xml': [           
        'security/sim_security.xml',
        'security/ir.model.access.csv',      
        'wizard/sim_move_create.xml',
        ## not working in 6.1
        #'wizard/print_traffic_detail.xml',
        'wizard/print_sim_location.xml',
        'res_sim_view.xml',
        'sim_sequence.xml',
        'report/reports.xml'
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
