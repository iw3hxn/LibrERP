# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    product_brand for OpenERP                                                  #
#    Copyright (C) 2009 NetAndCo (<http://www.netandco.net>).                   #
#    Authors, Mathieu Lemercier, mathieu@netandco.net,                          #
#             Franck Bret, franck@netandco.net                                  #
#    Copyright (C) 2011 Akretion Benoît Guillot <benoit.guillot@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################
from openerp.osv.orm import Model
from openerp.osv import fields


class product_brand(Model):
    _name = 'product.brand'
    
    _columns = {
        'name': fields.char('Brand Name', size=32),
        'description': fields.text('Description', translate=True),
        'partner_id': fields.many2one('res.partner', 'partner', help='Select a partner for this brand if it exist'),
        'logo': fields.binary('Logo File')
    }
    
    _order = 'name'
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the Brand must be unique !')
    ]

class product_template(Model):
    _name = 'product.template'
    _inherit = 'product.template'
    _columns = {
        'product_brand_id': fields.many2one('product.brand', 'Brand', help='Select a brand for this product'),
    }
    

class product_product(Model):
    _name = 'product.product'
    _inherit = 'product.product'
    
    def onchange_product_brand_id(self, cr, uid, ids, product_brand_id, context=None):
        """
        When category changes, we search for taxes, UOM and product type
        """
        context = context or self.pool['res.users'].context_get(cr, uid)

        res = {}

        if not product_brand_id:
            res = {
                'manufacturer': False,
            }
        else:
            brand_data = self.pool['product.brand'].browse(cr, uid, product_brand_id, context=context)
            if brand_data.partner_id:
                res['manufacturer'] = brand_data.partner_id.id
        return {'value': res, }

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        if context and context.get('product_brand_id', False):
            product_ids = self.pool['product.product'].search(cr, uid, [('product_brand_id', '=', context['product_brand_id'])])

            if product_ids:
                product_ids = list(set(product_ids))
                args.append(['id', 'in', product_ids])
        
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
