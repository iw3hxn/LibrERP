# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016-2019 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from openerp.osv import fields, orm


class AccountInvoice(orm.Model):
    _inherit = "account.invoice"

    def invoice_validate_check(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(AccountInvoice, self).invoice_validate_check(cr, uid, ids, context)
        show_except = not context.get('no_except', False)
        if not res:
            return False
        else:
            for invoice in self.browse(cr, uid, ids, context):

                if invoice.payment_term and invoice.payment_term.teamsystem_code == 0:
                    if show_except:
                        raise orm.except_orm('Fattura Cliente',
                                         'Impossibile da validare la fattura di {partner} in quanto sul termine di pagamento \'{payment}\' manca il codice TeamSystem'.format(partner=invoice.partner_id.name, payment=invoice.payment_term.name))
                    else:
                        return False
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.teamsystem_export:
                raise orm.except_orm(
                    'Errore!',
                    'La fattura è già stata esportata in teamsystem, chiedere lo sblocco'
                )
        return super(AccountInvoice, self).action_cancel(cr, uid, ids, context)

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        default = default or {}
        default.update({
            'teamsystem_export': False,
        })
        return super(AccountInvoice, self).copy(cr, uid, id, default, context)

    _columns = {
        'teamsystem_export': fields.boolean('Esportato in Teamsystem'),
    }


DIRECTIONS = [
    (0, 'Sinistra (0)'),
    (1, '1'),
    (2, '2')
]


class AccountJournal(orm.Model):
    _inherit = 'account.journal'
    _columns = {
        'teamsystem_code': fields.integer('Codice TeamSystem'),
        'teamsystem_invoice_position': fields.selection(DIRECTIONS, 'Posizione nella sequenza del numero')
    }


class AccountAccount(orm.Model):
    _inherit = 'account.account'
    _columns = {
        'teamsystem_code': fields.integer('Codice TeamSystem')
    }


class AccountPaymentTerm(orm.Model):
    _inherit = 'account.payment.term'
    _columns = {
        'teamsystem_code': fields.integer('Codice TeamSystem', required=False),
    }

    _sql_constraints = [('teamsystem_code_unique', 'unique(teamsystem_code)', 'Codice TeamSystem deve essere univoco')]


