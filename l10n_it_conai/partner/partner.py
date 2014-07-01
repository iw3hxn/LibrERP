# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech srl
#    (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from openerp.osv import orm, fields


class conai_declaration(orm.Model):
    _name = "conai.declaration"
    
    _columns = {
        'name': fields.char('Name', size=64),
        'number': fields.char('Number', size=64,),
        'percent_exemption': fields.float(
            'Exemption % (max 1.00 equal to 100%)', digits=(6, int(3))),
        'declaration_id': fields.integer('Declaration id', ),
        'partner_id': fields.many2one(
            'res.partner', 'Partner which declaration is linked'),
        'date_start_validity': fields.date('Date start validity'),
        'date_end_validity': fields.date('Date end validity'),
        'active': fields.boolean('Active',),
        'product_categ_id': fields.many2one(
            'product.category', 'Product category for which the declaration is valid'),
        'plafond_amount': fields.float('Amount of plafond', digits=(6, int(3))),
        'uom_id': fields.many2one('product.uom', 'UOM of plafond amount'),
    }

    _defaults = {
        'active': True,
    }


class res_partner(orm.Model):
    _inherit = "res.partner"
    
    _columns = {
        'name': fields.char('Name', size=64),
        'conai_declaration_ids': fields.one2many(
            'conai.declaration', 'declaration_id', 'CONAI declarations'),
        'is_conai_exempt': fields.boolean('Exempt for CONAI',),
    }
