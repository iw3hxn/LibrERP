# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2012 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2012-2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
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

from openerp.osv import orm, fields
from tools.translate import _


class account_move_line(orm.Model):
    _inherit = "account.move.line"
    _columns = {
        'vat_on_payment': fields.boolean(_('Vat on payment')),
        'tax_vat_on_payment_id': fields.many2one(
            'account.tax.code', _('VAT on Payment tax code for \
            reversal moves')),
        'account_vat_on_payment_id': fields.many2one(
            'account.account', _('VAT on Payment account for \
            reversal moves')),
    }
        

class account_move(orm.Model):
    _inherit = "account.move"
    _columns = {
        'journal_vat_on_payment_id': fields.many2one(
            'account.journal', _('Journal linked to vat on \
            payment move')),
    }
