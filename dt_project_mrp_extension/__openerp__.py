# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com) 
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
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
    'name': 'Procurement and Project Management integration extension',
    'version': '1.0',
    'category': 'Generic Modules/Projects & Services',
    'description': """
    
This module extends project_mrp that creates a link between procurement orders
containing "service" lines and project management tasks by adding the possibility
to create also new project from Sale Order.

The base module (project_mrp) will automatically create a new task
for each procurement order line, when the corresponding product
meets the following characteristics:
  * Type = Service
  * Procurement method (Order fulfillment) = MTO (make to order)
  * Supply/Procurement method = Produce

With this extension, you'll be able to :

  * Add tasks on existing project if "Project" field is fullfilled on the 
    Product of the SO line.

  * Add tasks on existing an project if "Analytic Account" field is fullfilled
    on the Sale Order.
    
    In those cases, the procurement is always related to the 
    task. When the project task is completed or cancelled, the workflow of the 
    corresponding procurement line is updated accordingly.
    Note that Project set in Product overwrite the Analytic Account set in the 
    order as it was done in project_mrp.
    
  * Create a new project if you let the "Analytic Account" field empty on the
    Sale Order. In that case, the procurement line is linked to the project and
    will be completed when the project will be done (closed). The project will
    be created from all Sale Order Line of type service and one task per line will 
    be associated to it.


""",
    'author': 'Camptocamp',
    'website': 'http://www.camptocamp.com',
    'depends': ['project_mrp','sale','procurement'],
    'init_xml': [],
    'update_xml': ['project_mrp_view.xml'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
