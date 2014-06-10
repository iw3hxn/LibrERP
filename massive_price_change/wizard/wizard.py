# -*- coding: utf-8 -*-

#       Copyright 2012 Francesco OpenCode Apruzzese <f.apruzzese@andreacometa.it>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from osv import fields,osv
from tools.translate import _

class wzd_massive_price_change(osv.osv_memory):

	_name = "wzd.massive_price_change"

	_columns = {
		'name' : fields.selection(
			(('mku', 'MarkUp'),('fix', 'Fix Price')),
			'Standard Price MarkUp Type'),
		'price_type': fields.selection(
			(('sale', 'Sale'),('cost', 'Cost')),
			'Price Type'),
		'value' : fields.float('Value', help="Insert a fix price or a value from 0 to 100 to markup old price"),
		}

	def change(self, cr, uid, ids, context={}):
		wzd = self.browse(cr, uid, ids[0], context)
		
		if wzd.price_type == 'sale':
			if wzd.name == 'fix':
				self.pool.get('product.product').write(cr, uid, context['active_ids'], {'list_price':wzd.value})
			else:
				product_obj = self.pool.get('product.product')
				for id in context['active_ids']:
					product = product_obj.browse(cr, uid, id, context)
					new_price = product.list_price + ((product.list_price * wzd.value) / 100.00)
					product_obj.write(cr, uid, [id, ], {'list_price':new_price})	
		else:
			if wzd.name == 'fix':
				self.pool.get('product.product').write(cr, uid, context['active_ids'], {'standard_price':wzd.value})
			else:
				product_obj = self.pool.get('product.product')
				for id in context['active_ids']:
					product = product_obj.browse(cr, uid, id, context)
					new_price = product.standard_price + ((product.standard_price * wzd.value) / 100.00)
					product_obj.write(cr, uid, [id, ], {'standard_price':new_price})
					
		return {'type': 'ir.actions.act_window_close'}

wzd_massive_price_change()
