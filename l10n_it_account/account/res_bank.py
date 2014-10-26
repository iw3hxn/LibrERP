# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech SRL
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

from openerp.osv import orm


class res_bank(orm.Model):
    _inherit = "res.bank"

    def on_change_city(self, cr, uid, ids, city, zip_code=None):
        res = self.pool['res.partner.address'].on_change_city(cr, uid, ids, city, zip_code=zip_code)
        return res

    def on_change_zip(self, cr, uid, ids, zip_code):
        res = self.pool['res.partner.address'].on_change_zip(cr, uid, ids, zip_code=zip_code)
        return res
