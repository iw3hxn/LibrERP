# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 - TODAY Denero Team. (<http://www.deneroteam.com>)
#    All Rights Reserved
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
from osv import fields, osv
import addons


class res_partner_title(osv.osv):
    _inherit="res.partner.title"
    _order = "sequence"
    _columns = {
        'sequence': fields.integer('Sequence'),
    }
    _defaults = {
        'sequence': 1,
    }
    
class res_contact_function(osv.osv):
    _name = "res.contact.function"
    _description = "Contact Function"
    _columns = {
        'name': fields.char('Name', size=32),
    }
    _order ="name"

class res_partner_address_contact(osv.osv):
    _name = "res.partner.address.contact"
    _description = "Address Contact"

    def _name_get_full(self, cr, uid, ids, prop, unknow_none, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = rec.last_name + ' ' + (rec.first_name or '')
        return result

    _columns = {
        'name': fields.function(_name_get_full, string='Name', size=64, type="char", store=True, select=True),
        'last_name': fields.char('Last Name', size=64, required=True),
        'first_name': fields.char('First Name', size=64),
        'mobile': fields.char('Mobile', size=64),
        'title': fields.many2one('res.partner.title', 'Title', domain=[('domain', '=', 'contact')]),
        'website': fields.char('Website', size=120),
        'address_id': fields.many2one('res.partner.address', 'Address'),
        'partner_id': fields.related('address_id', 'partner_id', type='many2one', relation='res.partner', string='Main Employer'),
        'lang_id': fields.many2one('res.lang', 'Language'),
        'country_id': fields.many2one('res.country', 'Nationality'),
        'birthdate': fields.char('Birthdate', size=64),
        'active': fields.boolean('Active', help="If the active field is set to False,\
                 it will allow you to hide the partner contact without removing it."),
        'email': fields.char('E-Mail', size=240),
        'comment': fields.text('Notes', translate=True),
        'photo': fields.binary('Photo'),
        #'function': fields.char("Function", size=64),
        'function_id': fields.many2one('res.contact.function', 'Function'),
        

    }

    def _get_photo(self, cr, uid, context=None):
        photo_path = addons.get_module_resource('base_address_contacts', 'images', 'photo.png')
        return open(photo_path, 'rb').read().encode('base64')

    _defaults = {
        'photo': _get_photo,
        'active': lambda *a: True,
    }

    _order = "name"

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=None):
        if not args:
            args = []
        if context is None:
            context = {}
        if name:
            ids = self.search(cr, uid, ['|', ('name', operator, name), ('first_name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.name or '/'
            if obj.partner_id:
                result[obj.id] = result[obj.id] + ', ' + obj.partner_id.name
        return result.items()

res_partner_address_contact()


class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    _columns = {
        'contact_ids': fields.one2many('res.partner.address.contact', 'address_id', 'Functions and Contacts'),
        'mobile': fields.char('Mobile', size=64),
        'pec': fields.char('PEC', size=64),
    }
res_partner_address()
