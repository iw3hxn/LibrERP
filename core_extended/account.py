# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author: Didotech SRL
#    Copyright 2015 Didotech SRL
#
#                       All Rights Reserved
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


class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'

    def _links_get(self, cr, uid, context=None):
        model_obj = self.pool['ir.model']
        ids = model_obj.search(cr, uid, [], context=context)
        res = model_obj.read(cr, uid, ids, ['model', 'name'], context)
        return [(r['model'], r['name']) for r in res]

    _columns = {
        'origin_document': fields.reference(_("Origin Document"), selection=_links_get, size=None)
    }
