# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech srl
#    (<http://www.didotech.com>).
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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import datetime


class account_tax(orm.Model):
    _inherit = 'account.tax'

    def onchange_tax_sign(self, cr, uid, ids, type_tax_use, context=None):
        if type_tax_use:
            if type_tax_use == "sale":
                return {'value': {'base_sign': 1, 'tax_sign': 1, 'ref_base_sign': -1, 'ref_tax_sign': -1}}
            elif type_tax_use == "purchase":
                return {'value': {'base_sign': -1, 'tax_sign': -1, 'ref_base_sign': 1, 'ref_tax_sign': 1}}
