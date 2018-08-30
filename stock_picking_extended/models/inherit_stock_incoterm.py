# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2014-2018 Didotech srl
#    (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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


class stock_incoterms(orm.Model):
    _inherit = "stock.incoterms"

    def name_get(self, cr, user, ids, context=None):

        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name', '')
            code = d.get('code', False)
            if code:
                name = '[%s] %s' % (code, name)
            return (d['id'], name)

        result = []
        for incoterm in self.read(cr, user, ids, ['id', 'name', 'code'], context=context):
            mydict = {
                'id': incoterm['id'],
                'name': incoterm['name'],
                'code': incoterm['code'],
            }
            result.append(_name_get(mydict))
        return result
