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

from openerp.osv import fields, orm


class wzd_invoice_massive_bank_change(orm.TransientModel):

	_name = "wzd.invoice.massive.bank.change"

	_columns = {
		'partner_bank_id': fields.many2one('res.partner.bank', 'Default Bank Account', help='' ),
		'also_not_draft': fields.boolean('Change also for not draft invoice')
	}

	def change(self, cr, uid, ids, context={}):
		wzd = self.browse(cr, uid, ids[0], context)
		res={}
		#import pdb
		#pdb.set_trace()
		bank_id = wzd.partner_bank_id
		res['partner_bank_id'] = bank_id.id
		

		self.pool['account.invoice'].write(cr, uid, context['active_ids'], res)
		return {'type': 'ir.actions.act_window_close'}

