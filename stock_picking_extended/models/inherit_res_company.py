# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product serial module for OpenERP
#    Copyright (C) 2016 Didotech srl (<http://www.didotech.com>).
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


class company(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'note_on_stock_move': fields.boolean('Copy Note on Move',
                                               help="Copy on stock move the note of sale order line"),
        'note_on_invoice_line': fields.boolean('Copy Note on Invoice', help="Copy on account invoice line the note of picking"),
        'required_minimum_planned_date': fields.boolean('Required Expected Date on Sale Order'),
    }


