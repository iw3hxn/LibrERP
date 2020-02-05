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


class wzd_massive_category_change(osv.osv_memory):
	_name = "wzd.massive_category_change"

	_columns = {
		'name': fields.many2one('product.category', 'Category'),
	}

	def change(self, cr, uid, ids, context=None):
		context = context or self.pool['res.users'].context_get(cr, uid)
		wzd = self.browse(cr, uid, ids[0], context)
		vals = {}
		categ = wzd.name
		vals['categ_id'] = categ.id

		if categ.provision_type:
			vals['type'] = categ.provision_type
		if categ.procure_method:
			vals['procure_method'] = categ.procure_method
		if categ.supply_method:
			vals['supply_method'] = categ.supply_method

		self.pool['product.product'].write(cr, uid, context['active_ids'], vals, context)
		return {'type': 'ir.actions.act_window_close'}
