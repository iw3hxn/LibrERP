# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Dhaval Patel (dhpatel82 at gmail.com)
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
    'name': 'Human Resources/Automobiles',
    'version': '2.0.1',
    'category': 'Generic Modules/Human Resources',
    'description': """A generic module for automobile car rental company to manage the employee and car""",
    "author": "Dhaval Patel",
    'depends': ['hr',
#                'web_google_map',
#                'web_gallery',
                ],
#    'init_xml': [],
    'update_xml': [
            'res_car_view.xml',
            'res_car_document_view.xml',
            'wizard/res_car_document_expiry_bymonth_view.xml',
            'res_auto_workflow.xml',
            'security/ir.model.access.csv',
            'data/res.car.service.type.csv',
            'data/res.car.document.type.csv',
            ],
    'demo_xml': [ 'res_car_demo.xml','res_car_document_demo.xml'  ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
