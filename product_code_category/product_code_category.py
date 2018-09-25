# -*- coding: utf-8 -*-
##############################################################################
#
#    product_code_category module for OpenERP, Generate product code when product was created
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of product_code_category
#
#    product_code_category is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    product_code_category is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from tools.translate import _
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class product_category(orm.Model):
    """
    Add a ir.sequence fields on category
    """
    _inherit = 'product.category'

    _columns = {
        'product_sequence_id': fields.many2one('ir.sequence', 'Product sequence', domain=[('code', '=', 'product.product')]),
    }

    _order = 'name, parent_id'


class product_supplierinfo(orm.Model):
    _inherit = 'product.supplierinfo'

    def _check_product_code(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for supplierinfo in self.browse(cr, uid, ids, context):
            if supplierinfo.product_code:
                res = self.search(cr, uid, [('product_code', '=', supplierinfo.product_code),
                                            ('name', '=', supplierinfo.name.id)
                                            ], context=context)
            else:
                res = []
            if supplierinfo.id in res:
                res.remove(supplierinfo.id)
            if len(res):
                _logger.error(u"Exist other product with code '{code}'".format(code=supplierinfo.product_code))
                raise orm.except_orm(_('Error!'),
                                     _(u"Exist other product with code '{code}'").format(code=supplierinfo.product_code))
        return True

    _constraints = [
        (_check_product_code, _('Duplicate code'), ['product_code'])
    ]


class product_product(orm.Model):
    """
    Add sequence on product on create with sequence
    assign by category
    """
    _inherit = 'product.product'

    def _check_defaultcode_and_variants(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for product in self.browse(cr, uid, ids, context):
            if product.default_code:
                res = self.search(cr, uid, [('default_code', '=', product.default_code),
                                            ('variants', '=', product.variants)
                                            ], context=context)
            else:
                res = []
            # Result may contain the current product if it's active: we remove it here.
            if product.id in res:
                res.remove(product.id)
            if len(res):
                # If we have any results left
                # we have duplicate entries
                if product.variants:
                    _logger.error(u"Exist other product with code '{code}' and variants'{variants}'".format(code=product.default_code, variants=product.variants))
                    raise orm.except_orm(_('Error!'), _(u"Exist other product with code '{code}' and variants'{variants}'").format(code=product.default_code, variants=product.variants))
                else:
                    _logger.error(u"Exist other product with code '{code}'".format(code=product.default_code))
                    raise orm.except_orm(_('Error!'), _(u"Exist other product with code '{code}'").format(code=product.default_code))
                return False
        return True

    _constraints = [
        (_check_defaultcode_and_variants, _('Duplicate code'), ['default_code', 'variants'])
    ]
    
    def _get_sequence(self, cr, uid, category_id, context=None):
        product_category_obj = self.pool['product.category']
        ir_sequence_obj = self.pool['ir.sequence']
        ir_model_data_obj = self.pool['ir.model.data']
        
        category = False
        
        # Recursive search for a sequence on the category
        while category_id is not False:
            category = product_category_obj.read(cr, uid, [category_id], ['product_sequence_id', 'parent_id'], context=context)
            category = category and category[0] or {}
            # If the category has a sequence, stop here
            if category.get('product_sequence_id', False):
                break

            # If the category has a parent, we continue on that parent, else, we stop
            category_id = category.get('parent_id', False)
            category_id = category_id and category_id[0] or False

        # If there is a sequence, we get its id
        if category and category.get('product_sequence_id', False):
            res = ir_sequence_obj.get_id(cr, uid, category['product_sequence_id'][0])
        # Else, we get the default product sequence
        else:
            # Assert the default sequence exists (this can be deleted)
            xml_id = self.pool.get('ir.model.data').search(cr, uid, [('module', '=', 'product_code_category'), ('name', '=', 'sequence_product_code_default')], context=context)
            if not xml_id:
                return ""

            sequence_data_id = ir_model_data_obj.get_object_reference(cr, uid, 'product_code_category', 'sequence_product_code_default')
            sequence_data_id = sequence_data_id and sequence_data_id[1]
            res = ir_sequence_obj.get_id(cr, uid, sequence_data_id)

        return res

    def create(self, cr, uid, vals, context=None):
        # If there is no default_code defined, we get a code from the category sequence
        if not vals.get('default_code', False):
            vals['default_code'] = self._get_sequence(cr, uid, vals.get('categ_id', False), context=context)

        res = super(product_product, self).create(cr, uid, vals, context=context)
        return res
    
    def copy(self, cr, uid, ids, default=None, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        if not default:
            default = {}
        
        # We want default code to be recreated:
        default['default_code'] = False
        
        return super(product_product, self).copy(cr, uid, ids, default, context)
 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
