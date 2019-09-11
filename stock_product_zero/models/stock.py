# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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
import logging
from openerp.osv import fields, orm
from tools.translate import _


class stock_location_product(orm.TransientModel):
    _inherit = "stock.location.product"
    _logger = logging.getLogger(__name__)
    _columns = {'display_with_zero_qty': fields.boolean('Display lines with zero')}

    def action_open_window_nok(self, cr, uid, ids, context=None):
        res = super(stock_location_product, self).action_open_window(cr, uid, ids, context=None)
        self._logger.debug('FGF stock_location_product action_open_window pre %s', res)

        location_products = self.read(cr, uid, ids, ['display_with_zero_qty'], context)
        # FIXME - I am not able to add display_with_zero_qty to context
        # raise osv.except_osv(_('FGF Warning !'), _('We check location_products:'))

        if location_products:
            res['context']['display_with_zero_qty'] = location_products['display_with_zero_qty']
        # self._logger.debug('FGF stock_location_product action_open_window post %s', res)
        return res

    def action_open_window(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = super(stock_location_product, self).action_open_window(cr, uid, ids, context)
        location_products = self.read(cr, uid, ids, ['display_with_zero_qty'], context)
        res['context']['display_with_zero_qty'] = location_products[0]['display_with_zero_qty']
        return res

    def action_open_window_nok2(self, cr, uid, ids, context=None):
        """ To open location wise product information specific to given duration
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: An ID or list of IDs if we want more than one
         @param context: A standard dictionary
         @return: Invoice type
        """
        # mod_obj = self.pool.get('ir.model.data')
        for location_obj in self.read(cr, uid, ids, ['from_date', 'to_date', 'display_with_zero_qty']):
            return {
                'name': False,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'product.product',
                'type': 'ir.actions.act_window',
                'context': {'location': context['active_id'],
                            'from_date': location_obj['from_date'],
                            'to_date': location_obj['to_date'],
                            'display_with_zero_qty': location_obj['display_with_zero_qty'],
                            },
                'domain': [('type', '!=', 'service')],
            }


class product_product(orm.Model):
    _inherit = "product.product"
    _logger = logging.getLogger(__name__)

    # FIXME this returns correct records, but group by catagory ignores this and uses all results for grouping
    # opening a category crashes
    def read_test(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        res_all = super(product_product, self).read(cr, uid, ids, fields, context, load='_classic_read')
        res = []
        self._logger.debug('FGF stock_location_product read ids %s', res_all)
        if context.get('display_with_zero_qty') and context.get('display_with_zero_qty') is False:
            self._logger.debug('FGF stock_location_product read  only not null')
            for prod in self.browse(cr, uid, res_all):
                qty = prod.get('qty_available')
                vir = prod.get('virtual_available')
                if qty != 0.0 or vir != 0.0:
                    res.append(prod)
        else:
            self._logger.debug('FGF stock_location_product  all')
        res = res_all
        # FIXME - result should be sorted by name
        # http://wiki.python.org/moin/SortingListsOfDictionaries - returns (unicode?) error on name
        return res

    def not_0(self, cr, uid, digits, context):
        to_check = context.get('to_check')
        for t in to_check:
            if round(t, digits) != 0.0:
                return True
        return False

    def fields_to_check(self, cr, uid):
        fields = ['qty_available', 'virtual_available']
        return fields

    def search_0(self, cr, uid, res, context):
        res2 = []
        digits = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product UoM')
        for prod in self.browse(cr, uid, res, context):
            to_check = []
            for v in self.fields_to_check(cr, uid):
                v1 = eval('prod.' + v)
                to_check.append(v1)
            context['to_check'] = to_check
            if self.not_0(cr, uid, digits, context):
                res2.append(prod.id)
        return res2

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if not context: context = {}
        res = []
        if not context.get('location') or context.get('display_with_zero_qty', True):
            res = super(product_product, self).search(cr, uid, args, offset, limit, order, context, count)
        else:
            # FIXME how to handle offset and limit
            res_all = super(product_product, self).search(cr, uid, args, None, None, order, context, count)
            res = self.search_0(cr, uid, res_all, context)

        return res
