# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 ISA srl (<http://www.isa.it>).
#    Copyright (C) 2013 Sergio Corato (<http://www.icstools.it>).
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

import time
from openerp.osv import fields, orm
from tools.translate import _


class account_invoice(orm.Model):

    _inherit = 'account.invoice'

    def _maturity(self, cr, uid, ids, filed_name, arg, context=None):
        res = {}
        for o in self.browse(cr, uid, ids, context):
            if not o.id in res:
                res[o.id] = []
            if o.move_id and o.move_id.line_id:
                for line in o.move_id.line_id:
                    if line.date_maturity:
                        res[o.id].append(line.id)
        return res
    
    _columns = {
        'registration_date': fields.date('Registration Date', states={'paid': [('readonly', True)], 'open': [('readonly', True)], 'close': [('readonly', True)]}, select=True, help="Keep empty to use the current date"),
        'maturity_ids': fields.function(
            _maturity, type="one2many", store=False,
            relation="account.move.line", method=True)
    }
    
    def action_move_create(self, cr, uid, ids, context=None):
        super(account_invoice, self).action_move_create(cr, uid, ids, context=context)
        for inv in self.browse(cr, uid, ids):
            date_invoice = inv.date_invoice
            reg_date = inv.registration_date
            if not inv.registration_date:
                if date_invoice:
                    reg_date = date_invoice
                else:
                    reg_date = time.strftime('%Y-%m-%d')
            if date_invoice and reg_date:
                if (date_invoice > reg_date):
                    raise orm.except_orm(_('Error date !'), _('The invoice date cannot be later than the date of registration!'))
            #periodo
            date_start = inv.registration_date or inv.date_invoice or time.strftime('%Y-%m-%d')
            date_stop = inv.registration_date or inv.date_invoice or time.strftime('%Y-%m-%d')
            period_ids = self.pool['account.period'].search(
                cr, uid, [('date_start', '<=', date_start), ('date_stop', '>=', date_stop), ('company_id', '=', inv.company_id.id)])
            if period_ids:
                period_id = period_ids[0]
                self.write(cr, uid, [inv.id], {'registration_date': reg_date, 'period_id': period_id})
                mov_date = reg_date or inv.date_invoice or time.strftime('%Y-%m-%d')
                self.pool['account.move'].write(cr, uid, [inv.move_id.id], {'state': 'draft'})
                if inv.supplier_invoice_number:
                    sql = "update account_move_line set period_id = " + \
                        str(period_id) + ", date = '" + mov_date + "' , ref = '" + \
                        inv.supplier_invoice_number + "' where move_id = " + str(inv.move_id.id)
                else:
                    sql = "update account_move_line set period_id = " + \
                        str(period_id) + ", date = '" + mov_date + "' where move_id = " + str(inv.move_id.id)
                cr.execute(sql)
                if inv.supplier_invoice_number:
                    self.pool['account.move'].write(
                    cr, uid, [inv.move_id.id], {
                        'period_id': period_id,
                        'date': mov_date,
                        'ref': inv.supplier_invoice_number})
                else:
                    self.pool['account.move'].write(
                        cr, uid, [inv.move_id.id], {'period_id': period_id, 'date': mov_date})
                self.pool['account.move'].write(cr, uid, [inv.move_id.id], {'state': 'posted'})

        self._log_event(cr, uid, ids)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        if 'registration_date' not in default:
            default.update({
                'registration_date': False
            })
        return super(account_invoice, self).copy(cr, uid, id, default, context)
