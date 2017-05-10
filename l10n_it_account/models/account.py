# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


PAYMENT_TERM_TYPE_SELECTION = [
    ('BB', 'Bonifico Bancario'),
    ('BP', 'Bonifico Postale'),
    ('RD', 'Rimessa Diretta'),
    ('RB', 'Ricevuta Bancaria'),
    ('F4', 'F24'),
    ('PP', 'Paypal'),
    ('CC', 'Carta di Credito'),
    ('CO', 'Contrassegno'),
    ('CN', 'Contanti'),
    ('SD', 'Sepa DD'),
]


class account_payment_term(orm.Model):
    _inherit = 'account.payment.term'
    _columns = {
        'type': fields.selection(PAYMENT_TERM_TYPE_SELECTION, "Type of payment"),
    }
