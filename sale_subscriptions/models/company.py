
##############################################################################
#
#    Author: Didotech SRL
#    Copyright 2015 Didotech SRL
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

from openerp.osv import orm, fields
from tools.translate import _


class ResCompany(orm.Model):

    _inherit = 'res.company'

    _columns = {
        'subscription_invoice_day': fields.selection((
            ('1', _('First day of month')),
            ('31', _('Last day of month'))
        ), _('Invoice Day')),
    }

    _defaults = {
        'subscription_invoice_day': 1
    }
