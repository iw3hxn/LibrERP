
##############################################################################
#
#    Author: Jo?l Grand-Guillaume, Guewen Baconnier
#    Copyright 2010-2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv


class res_company(osv.osv):

    _inherit = 'res.company'

    _columns = {
        'ref_stock': fields.selection(
            [('real', 'Real Stock'),
             ('virtual', 'Virtual Stock'),
             ('immediately', 'Immediately Usable Stock')],
            'Reference Stock for BoM Stock')
    }

    _defaults = {
        'ref_stock': lambda *a: 'real'
    }
