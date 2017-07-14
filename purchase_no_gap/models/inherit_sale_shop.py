# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Alejandro Núñez Liz$
#    $Omar Castiñeira Saavedra$
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from tools import ustr
from tools.translate import _


class sale_shop(orm.Model):
    _inherit = 'sale.shop'

    _columns = {
        'purchase_sequence_id': fields.many2one('ir.sequence', 'Purchase Entry Sequence',
                                       help="This field contains the information related to the numbering of the Purchase Orders.",
                                       domain="[('code', '=', 'purchase.order')]"),
        'purchase_confirmed_sequence_id': fields.many2one('ir.sequence', 'Purchase Entry Sequence Confirmed',
                                                  help="This field contains the information related to the numbering of the Purchase Orders Confirmed",
                                                  domain="[('code', '=', 'purchase.order')]"),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if isinstance(ids, (int, long)):
            ids = [ids]
        if vals.get('purchase_sequence_id', False) and vals.get('purchase_confirmed_sequence_id', False):
            if vals.get('purchase_sequence_id', False) == vals.get('purchase_confirmed_sequence_id', False):
                raise orm.except_orm(_('Error!'),
                                     _("In not possible to have same sequence"))

        return super(sale_shop, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if vals.get('purchase_sequence_id', False) and vals.get('purchase_confirmed_sequence_id', False):
            if vals.get('purchase_sequence_id', False) == vals.get('purchase_confirmed_sequence_id', False):
                raise orm.except_orm(_('Error!'),
                                     _("In not possible to have same sequence"))

        return super(sale_shop, self).create(cr, uid, vals, context=context)

