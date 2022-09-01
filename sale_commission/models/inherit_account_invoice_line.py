# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
# $Id$
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

"""invoice agents"""

from openerp.osv import orm, fields
from tools.translate import _


class account_invoice_line(orm.Model):
    """Enlazamos las comisiones a la factura"""

    _inherit = "account.invoice.line"

    _columns = {
        'commission_ids': fields.one2many('invoice.line.agent', 'invoice_line_id', 'Commissions',
                                          help="Commissions asociated to invoice line."),
    }

    def copy_data(self, cr, uid, ids, default=None, context=None):
        if not default:
            default = {}
        default.update({'commission_ids': False})
        return super(account_invoice_line, self).copy_data(cr, uid, ids, default, context=context)

