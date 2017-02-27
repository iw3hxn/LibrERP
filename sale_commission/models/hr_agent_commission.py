# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
# $Id$
#
# This program is free software: you can redistribute it and/or modify
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


class hr_agent_commission(orm.Model):
    _name = 'hr.agent.commission'
    _description = 'Commission'
    _columns = {
        'name': fields.char('Name'),
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade'),
        'category_id': fields.many2one('product.category', 'Category Product\'s', ondelete='cascade'),
        'customer_id': fields.many2one('res.partner', 'Customer', ondelete='cascade'),
        'commission_percent': fields.float('Commission (%)', digits=(5, 2)),
        'fixed_commission': fields.float('fixed commission', digits=(10, 2)),
        'commission_id': fields.many2one('commission', 'Applied commission'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

