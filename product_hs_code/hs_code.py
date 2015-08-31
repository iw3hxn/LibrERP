# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2015 Didotech SRL (info @ didotech.com).
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
import re
from tools.translate import _

#----------------------------------------------------------
# Categories
#----------------------------------------------------------

class hs_category(orm.Model):

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.browse(cr, uid, ids, context=context)
        res = []
        for record in reads:
            name = record.name
            if record.parent_id:
                name = record.parent_id.name + ' / ' + name
            res.append((record.id, name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _name = "hs.category"
    _description = "HS Category"
    _columns = {
        'code': fields.integer('Code', help="HS Code"),
        'name': fields.char('Name', size=256, required=True, translate=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
        'parent_id': fields.many2one('hs.category', 'Parent Category', select=True),
        'child_id': fields.one2many('hs.category', 'parent_id', string='Child Categories'),
        'type': fields.selection([('view', 'View'), ('normal', 'Normal')], 'Category Type'),
    }

    _defaults = {
        'type': lambda *a: 'normal',
    }

    _order = "code"

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from hs_category where id IN %s', (tuple(ids),))
            ids = filter(None, map(lambda x: x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
    ]

    def child_get(self, cr, uid, ids):
        return [ids]


#----------------------------------------------------------
# HS Codes
#----------------------------------------------------------

class hs_code(orm.Model):

    # def view_header_get(self, cr, uid, view_id, view_type, context=None):
    #     if context is None:
    #         context = {}
    #     res = super(hs_code, self).view_header_get(cr, uid, view_id, view_type, context)
    #     if context.get('categ_id', False):
    #         return _('HS: ') + self.pool['hs.category'].browse(cr, uid, context['categ_id'], context=context).name
    #     return res

    _defaults = {
        'active': lambda *a: 1,
    }

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = '[%s] %s' % (record.code, record.name)
            if record.variants:
                name = name + ': ' + record.variants
            res.append((record.id, name))

        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _name = "hs.code"
    _description = "HS Codes"
    _table = "hs_code"
    _order = 'code, name'
    _columns = {
        'code': fields.char('Code', size=10),
        'name': fields.char('Name', size=256, required=True, translate=True, select=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Complete Name'),
        'active': fields.boolean('Active',
                                 help="If the active field is set to False, it will allow you to hide the HS Code without removing it."),
        'variants': fields.char('Variants', size=64),
        'description': fields.text('Description'),
        'category_id': fields.many2one('hs.category', 'Category', required=True, change_default=True,
                                    help="Category for the current HS Code"),
        'current_products': fields.one2many('product.product', 'hs_id', 'Current Products'),
        'duty_free_tl': fields.float('Duty Free TL (%)'),
        'custom_rate': fields.float('Exchange Rate'),
    }

    def on_order(self, cr, uid, ids, orderline, quantity):
        pass

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):

        if not args:
            args = []
        ids = []
        if name:
            ids = self.search(cr, user, [('code', '=', name)] + args, limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
                ids += self.search(cr, user, [('variants', operator, name)] + args, limit=limit, context=context)
            if not len(ids):
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('code', '=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result



#----------------------------------------------------------
# Products
#----------------------------------------------------------

class product_product(orm.Model):
    _inherit = 'product.product'
    _columns = {
        'hs_id': fields.many2one('hs.code', 'HS Code'),
    }

