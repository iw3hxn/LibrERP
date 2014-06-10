# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from osv import fields, osv


class account_payment_term_type(osv.osv):
	
	_name = 'account.payment.term.type'
	_description = 'Payment term type list'

	_columns = {
		'name' : fields.char('Codice', size=16),
		'description' : fields.char('Descrizione', size=64),
	}

account_payment_term_type()


class account_payment_term(osv.osv):
	
	_name = 'account.payment.term'
	_inherit = 'account.payment.term'

	_columns = {
		'payment_term_type' : fields.many2one('account.payment.term.type', 'Tipo di pagamento'),
	}

account_payment_term()


class account_move_line(osv.osv):

	_name = 'account.move.line'
	_inherit = 'account.move.line'

	def _importo(self, cr, uid, ids, name, arg, context=None):
		res = {}
		for line in self.browse(cr, uid, ids, context=context):
			if line.reconcile_partial_id:
				total_line = 0.0
				for line_reconcile in line.reconcile_partial_id.line_partial_ids:
					total_line += line_reconcile.debit - line_reconcile.credit
				res[line.id] = total_line
			else:
				res[line.id] = line.debit - line.credit
		return res

	def _payment_type(self, cr, uid, ids, name, arg, context=None):
		res = {}
		for line in self.browse(cr, uid, ids, context=context):
			res[line.id] = line.payment_term_id and line.payment_term_id.payment_term_type and line.payment_term_id.payment_term_type.id or False
		return res

	def _payment_term_search(self, cr, uid, obj, name, args, context):
		if args:
			payment_obj = self.pool.get('account.payment.term')
			payment_ids = payment_obj.search(cr, uid, args)
			if payment_ids:
				move_ids = self.search(cr, uid, [('payment_term_id', 'in', payment_ids)])
				return [('id', 'in', move_ids)]
		return False
		
	_columns = {
		'payment_term_type' : fields.function(_payment_type, method=True, string='Tipo di pagamento', type='many2one',
			relation='account.payment.term.type', store=False,
			fnct_search=_payment_term_search),
		'importo' : fields.function(_importo, method=True, string='Importo', type='float', store=False),
		}

account_move_line()
