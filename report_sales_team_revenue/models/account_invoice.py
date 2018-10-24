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


class account_invoice(orm.Model):

    _inherit = "account.invoice"

    _columns = {
        'section_id': fields.many2one('crm.case.section', 'Sales Team', states={'draft': [('readonly', False)]},
                                      required=[('type', 'in', ['out_invoice', 'out_refund'])]),
    }

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # NEED TO BE SURE TO HAVE SALES TEAM WITH VALUE
        if not vals.get('section_id', False) and vals.get('type') in ['out_invoice', 'out_refund']:
            section = self.pool['res.partner'].browse(cr, uid, vals.get('partner_id'), context).section_id
            if section:
                vals.update({'section_id': section.id})
        return super(account_invoice, self).create(cr, uid, vals, context)
