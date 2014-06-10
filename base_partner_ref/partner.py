# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 Numérigraphe SARL.
#                 ,2013 Didotech SRL
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

from openerp.osv import orm, fields

class partner(orm.Model):
    _inherit = 'res.partner'
    _columns = {
        'property_supplier_ref': fields.char('Supplier Ref.', size=16, help="The reference attributed by the partner to the current company as a supplier of theirs."),
        'property_customer_ref': fields.char('Customer Ref.', size=16, help="The reference attributed by the partner to the current company as a customer of theirs."),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
