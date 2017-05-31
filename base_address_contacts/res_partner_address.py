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
from openerp.osv import orm, fields
from openerp import addons
from openerp.tools.translate import _

class res_partner_title(orm.Model):
    _inherit = "res.partner.title"
    _order = "sequence"
    _columns = {
        'sequence': fields.integer('Sequence'),
    }
    _defaults = {
        'sequence': 1,
    }


class res_contact_function(orm.Model):
    _name = "res.contact.function"
    _description = "Contact Function"
    _order = "name"
    _columns = {
        'name': fields.char('Name', size=32),
    }


class res_partner_address_contact(orm.Model):
    _name = "res.partner.address.contact"
    _description = "Address Contact"

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for rec in self.browse(cr, uid, ids, context=context):
            name = u"{name} {surname}".format(name=rec.last_name or '', surname=rec.first_name or '')
            if rec.title:
                name = rec.title.name + name
            res.append((rec.id, name))
        return res

    def _name_get_full(self, cr, uid, ids, prop, unknow_none, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            name = u"{name} {surname}".format(name=rec.last_name or '', surname=rec.first_name or '')
            if rec.title:
                name = u"{title} {name}".format(title=rec.title.name, name=name)
            result[rec.id] = name
        return result

    _columns = {
        'complete_name': fields.function(_name_get_full, string='Name', size=64, type="char", store=False, select=True),
        'name': fields.char('Name', size=64, ),
        'last_name': fields.char('Last Name', size=64),
        'first_name': fields.char('First Name', size=64),
        'mobile': fields.char('Mobile', size=64),
        'fisso': fields.char('Phone', size=64),
        'title': fields.many2one('res.partner.title', 'Title', domain=[('domain', '=', 'contact')]),
        'website': fields.char('Website', size=120),
        'address_id': fields.many2one('res.partner.address', 'Address'),
        'partner_id': fields.related(
            'address_id', 'partner_id', type='many2one', relation='res.partner', string='Main Employer'),
        'lang_id': fields.many2one('res.lang', 'Language'),
        'country_id': fields.many2one('res.country', 'Nationality'),
        'birthdate': fields.char('Birthdate', size=64),
        'active': fields.boolean('Active', help="If the active field is set to False,\
                 it will allow you to hide the partner contact without removing it."),
        'email': fields.char('E-Mail', size=240),
        'comment': fields.text('Notes', translate=True),
        'photo': fields.binary('Photo'),
        'function': fields.char("Function", size=64),
        'function_id': fields.many2one('res.contact.function', 'Function'),
    }

    def _get_photo(self, cr, uid, context=None):
        photo_path = addons.get_module_resource('base_address_contacts', 'images', 'photo.png')
        return open(photo_path, 'rb').read().encode('base64')

    _defaults = {
        'name': '/',
        'photo': _get_photo,
        'active': True,
        'address_id': lambda self, cr, uid, context: context.get('address_id', False),
    }

    _order = "last_name"

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=None):
        if not args:
            args = []
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if name:
            ids = self.search(
                cr, uid, ['|', ('last_name', operator, name), ('first_name', operator, name)] + args, limit=limit,
                context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context=context)

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        name = ''
        update = False

        if vals.get('last_name', False):
            name += vals['last_name']
            update = True

        if vals.get('first_name', False):
            name += ' ' + vals['first_name']
            update = True

        if update:
            vals['name'] = name

        return super(res_partner_address_contact, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        name = ''
        update = False

        if vals.get('last_name', False):
            name += vals['last_name']
            update = True
            
        if vals.get('first_name', False):
            name += ' ' + vals['first_name']
            update = True

        if update:
            vals['name'] = name
                    
        return super(res_partner_address_contact, self).write(cr, uid, ids, vals, context)


class res_partner_address(orm.Model):
    _inherit = 'res.partner.address'

    def get_full_name(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for re in self.browse(cr, uid, ids, context=context):
            addr = ''
            if re.partner_id:
                if re.partner_id.name != re.name:
                    addr = re.name or ''
                    if re.name and (re.city or re.country_id):
                        addr += ', '
            addr += (re.city or '') + ', ' + (re.street or '')
            if re.partner_id and context.get('contact_display', False) == 'partner_address':
                addr = "%s: %s" % (re.partner_id.name, addr.strip())
                # addr = re.partner_id.name + ': ' + addr
            else:
                addr = addr.strip()
            res[re.id] = addr or ''
        return res

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        if not context:
            context = self.pool['res.users'].context_get(cr, uid)
        length = context.get('name_lenght', False) or 80
        for record in self.browse(cr, uid, ids, context=context):
            name = record.complete_name or record.name or ''
            # if len(name) > length:
            #    name = name[:length] + '...'
            res.append((record.id, name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        ids = []
        name_array = name.split()
        search_domain = []
        for n in name_array:
            partner_ids = self.pool['res.partner'].search(cr, uid, [('name', operator, name)], limit=limit, context=context)
            search_domain.append('|')
            search_domain.append(('partner_id', 'in', partner_ids))
            search_domain.append(('name', operator, n))
            search_domain.append(('complete_name', operator, n))

        ids = self.search(cr, uid, search_domain + args, limit=limit, context=context)
        context['contact_display'] = 'partner_address'
        return self.name_get(cr, uid, ids, context=context)

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner Name', ondelete='set null', select=True, help="Keep empty for a private address, not related to partner.", required=True),
        'contact_ids': fields.one2many('res.partner.address.contact', 'address_id', 'Functions and Contacts'),
        'mobile': fields.char('Mobile', size=64),
        'pec': fields.char('PEC', size=64),
        'complete_name': fields.function(get_full_name, method=True, type='char', size=1024, readonly=True, store=False),
    }


class res_partner(orm.Model):
    _inherit = 'res.partner'
    
    def _get_contacts(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        
        for partner in self.browse(cr, uid, ids, context):
            result[partner.id] = []
            for address in partner.address:
                result[partner.id] += [contact.id for contact in address.contact_ids]
            
        return result

    def create(self, cr, uid, vals, context):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if context.get('import', False):
            return super(res_partner, self).create(cr, uid, vals, context)
        if not vals.get('address', False) and context.get('default_type', '') != 'lead' and not context.get('install_mode', False): 
            raise orm.except_orm(_('Error!'),
                                 _('At least one address of type "Default" is needed!'))
        is_default = False
        if context.get('default_type', '') == 'lead':
            return super(res_partner, self).create(cr, uid, vals, context)
        if vals.get('address', False):
            for address in vals['address']:
                if address[2].get('type') == 'default':
                    is_default = True
        if not is_default and not context.get('install_mode', False):
            raise orm.except_orm(_('Error!'),
                                 _('At least one address of type "Default" is needed!'))

        return super(res_partner, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if vals.get('address', False):
            for address in vals['address']:
                if address[0] == 2: # 2 means 'delete'
                    if self.pool['res.partner.address'].browse(cr, uid, address[1], context).type == 'default':
                        raise orm.except_orm(_('Error!'),
                                             _('At least one address of type "Default" is needed!'))

        return super(res_partner, self).write(cr, uid, ids, vals, context)

    def unlink(self, cr, uid, ids, context):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        for partner in self.browse(cr, uid, ids, context):
            if partner.address:
                raise orm.except_orm(_('Error!'),
                                 _('Before Delete the Partner, you need to delete the Address from menù'))
        return super(res_partner, self).unlink(cr, uid, ids, context)

    _columns = {
        'contact_ids': fields.function(_get_contacts, string=_("Functions and Contacts"), type='one2many', method=True, obj='res.partner.address.contact')
    }
