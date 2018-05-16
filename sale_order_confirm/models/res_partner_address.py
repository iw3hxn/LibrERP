# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyraght (c) 2013-2016 Didotech srl (<http://www.didotech.com>)
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
from openerp.tools.translate import _


class res_partner_address(orm.Model):
    _inherit = "res.partner.address"

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # check if there are same sale order connected
        sale_order_ids = self.pool['sale.order'].search(cr, uid, ['|', '|', ('partner_order_id', 'in', ids), ('partner_invoice_id', 'in', ids), ('partner_shipping_id', 'in', ids)], context=context)
        if sale_order_ids:
            title = _(u'Error')
            msg = _(u'Is not possible to Delete Address because exist a connected Sale Order')
            raise orm.except_orm(title, msg)
        return super(res_partner_address, self).unlink(cr, uid, ids, context)
