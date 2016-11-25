# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2012 DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2011-2013 Didotech Srl. (<http://www.didotech.com>)
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
##############################################################################.

from openerp.osv import orm, fields
import sys
import traceback
from tools.translate import _
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


COLOR_SELECTION = [
    ('aqua', _(u"Aqua")),
    ('black', _(u"Black")),
    ('blue', _(u"Blue")),
    ('brown', _(u"Brown")),
    ('cadetblue', _(u"Cadet Blue")),
    ('darkblue', _(u"Dark Blue")),
    ('fuchsia', _(u"Fuchsia")),
    ('forestgreen', _(u"Forest Green")),
    ('green', _(u"Green")),
    ('grey', _(u"Grey")),
    ('red', _(u"Red")),
    ('orange', _(u"Orange"))
]


class project_plant_type(orm.Model):
    _name = "project.plant.type"
    
    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        uses = self.browse(cr, uid, ids)
        for use in uses:
            if use.color:
                value[use.id] = use.color
            else:
                value[use.id] = 'black'
        return value

    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'color': fields.selection(COLOR_SELECTION, 'Color'),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True,),
        'department_ids': fields.many2many("hr.department", "hr_department_project_plant_type_rel", "plant_type_id", "department_id", "Departments"),
    }
    _defaults = {
        'name': lambda self, cr, uid, context: self.pool.get('ir.sequence').get(cr, uid, 'project.plant.type'),
    }
    _order = "name"
    _sql_constraints = [('name_uniq', 'unique(name)', 'Name must be unique!')]


class project_place_type(orm.Model):
    _name = "project.place.type"
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'need_more_info': fields.boolean("Need More Info"),
    }
    _order = "id"
    _sql_constraints = [('name_uniq', 'unique(name)', 'Name must be unique!')]


class project_agreement_type(orm.Model):
    _name = "project.agreement.type"
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
    }
    _sql_constraints = [('name_uniq', 'unique(name)', 'Name must be unique!')]


class res_partner_address(orm.Model):
    _inherit = 'res.partner.address'
    _rec_name = 'complete_name'
    
    def get_full_name(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for re in self.browse(cr, uid, ids, context=context):
            addr = ''
            if re.type in ['plant', 'place']:
                addr = "[%s] %s " % (re.type, re.name)
            else:
                if re.partner_id:
                    if re.partner_id.name != re.name:
                        addr = re.name or ''
                        if re.name and (re.city or re.country_id):
                            addr += ', '
            addr += (re.city or '') + ', ' + (re.street or '')
            if re.partner_id and context.get('contact_display', False) == 'partner_address':
                addr = "%s: %s" % (re.partner_id.name, addr.strip())
            else:
                addr = addr.strip()
            res[re.id] = addr or ''
        return res
    
    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.complete_name or record.name or ''
            # if len(name) > 45:
            #     name = name[:45] + '...'
            res.append((record.id, name))
        return res
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        name_array = name.split()
        search_domain = []
        for n in name_array:
            search_domain.append('|')
            search_domain.append(('name', operator, n))
            search_domain.append(('complete_name', operator, n))
        ids = self.search(cr, user, search_domain + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)
    
    _columns = {
        'type': fields.selection(
            [
                ('default', (u'Default')),
                ('invoice', (u'Invoice')),
                ('delivery', (u'Delivery')),
                ('contact', (u'Contact')),
                ('plant', (u'Plant')),
                ('place', (u'Place')),
                ('other', (u'Other')),
            ], 'Address Type', help="Used to select automatically the right address according to the context in sales and purchases documents."),

        'complete_name': fields.function(get_full_name, method=True, type='char', size=1024, readonly=True, store=False),
    }


class plant_property_group(orm.Model):
    _name = 'plant.property.group'
    _description = 'Property Group'
    _columns = {
        'name': fields.char('Property Group', size=64, required=True),
        'description': fields.text('Description'),
    }


class project_plant(orm.Model):
    _name = "project.plant"
    _inherits = {'res.partner.address': 'address_id'}
    _rec_name = 'code'
    
    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        plants = self.browse(cr, uid, ids, context)
        for plant in plants:
            if plant.plant_type_id:
                value[plant.id] = plant.plant_type_id.color
            else:
                value[plant.id] = 'black'

        return value
    
    def _get_plant_employees(self, cr, uid, ids, prop, unknow_none, context=None):
        if not len(ids):
            return {}
        res = []
        try:
            for plant in self.browse(cr, uid, ids, context=context):
                employee_ids = []
                plant_type_id = plant.plant_type_id.id
                if not plant_type_id:
                    continue
                ptype = self.pool['project.plant.type'].browse(cr, uid, plant_type_id, context=context)
                for department in ptype.department_ids:
                    #employee_ids += [department.manager_id.id]
                    employee_ids += map(lambda e: e.id, department.member_ids)
                res.append((plant.id, employee_ids))
        except:
            _logger.error('%s' % (repr(traceback.extract_tb(sys.exc_traceback))))
        return dict(res)
    
    def get_plant_departments(self, cr, uid, ids, context=None):
        if not len(ids):
            return {}
        res = []
        try:
            for plant in self.browse(cr, uid, ids, context=context):
                department_ids = []
                plant_type_id = plant.plant_type_id.id
                if not plant_type_id:
                    continue
                ptype = self.pool['project.plant.type'].browse(cr, uid, plant_type_id, context=context)
                for department in ptype.department_ids:
                    department_ids.append(department.id)
                res.append((plant.id, department_ids))
        except:
            _logger.error('%s' % (repr(traceback.extract_tb(sys.exc_traceback))))
        return dict(res)
        
    def _get_moved_products_in(self, cr, uid, ids, prop, unknow_none, context=None):
        if not len(ids):
            return {}
        res = []
        try:
            for plant in self.browse(cr, uid, ids, context):
                res.append((plant.id, self.pool['stock.move'].search(cr, uid, [('location_dest_id', '=', plant.stock_location_id and plant.stock_location_id.id or '')])))
        except:
            _logger.error('%s' % (repr(traceback.extract_tb(sys.exc_traceback))))
        return dict(res)
        
    def _get_moved_products_out(self, cr, uid, ids, prop, unknow_none, context=None):
        if not len(ids):
            return {}
        res = []
        try:
            for plant in self.read(cr, uid, ids, ['stock_location_id'], context):
                if plant['stock_location_id']:
                    res.append((plant['id'], self.pool.get('stock.move').search(cr, uid, [('location_id', '=', plant['stock_location_id'][0])])))
        except:
            _logger.error('%s' % (repr(traceback.extract_tb(sys.exc_traceback))))
        return dict(res)
    
    def _get_assigned_assets(self, cr, uid, ids, field_name, arg, context=None):
        return self.pool.get('asset.asset').get_current_assigned_assets(cr, uid, ids, field_name, self._name, context)
    
    def _get_default_address(self, cr, uid, field, context=None):
        if context.get('default_place_id', False):
            places = self.pool['project.place'].read(cr, uid, context['default_place_id'], [field])
            if places:
                return places[field]
        
        return

    _columns = {
        'code': fields.char('Code', size=64),
        'address_id': fields.many2one('res.partner.address', "Address", required=True, ondelete='cascade'),
        'plant_type_id': fields.many2one("project.plant.type", "Plan Type"),
        'plant_agreement_id': fields.many2one("project.agreement.type", "Agreement Type"),
        'ticket_close_time_out': fields.float('Time Out to Close Ticket', size=8, help="Time Out to Close Ticket"),
        'ticket_approve_time_out': fields.float('Time Out to Approve Ticket', size=8, help="Time Out to Approve Ticket"),
        'member_ids': fields.function(_get_plant_employees, method=True, string='Members', type='one2many', relation="hr.employee"),
        'stock_location_id': fields.many2one('stock.location', 'Stock Location', readonly=True),
        'stock_move_in_ids': fields.function(_get_moved_products_in, method=True, string='Products In', type='one2many', relation="stock.move"),
        'stock_move_out_ids': fields.function(_get_moved_products_out, method=True, string='Products Out', type='one2many', relation="stock.move"),
        'asset_ids': fields.function(_get_assigned_assets, method=True, string='Assets', type='one2many', relation="asset.asset"),
        'property_ids': fields.one2many('plant.property', 'plant_id', 'Properties'),
        'place_id': fields.many2one("project.place", "Place"),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True,),
    }
    
    _defaults = {
        'code': '/',  # lambda self, cr, uid, context: self.pool.get('ir.sequence').get(cr, uid, 'project.plant'),
        'type': 'plant',
        'street': lambda self, cr, uid, context: self._get_default_address(cr, uid, 'street', context),
        'street2': lambda self, cr, uid, context: self._get_default_address(cr, uid, 'street2', context),
        'city': lambda self, cr, uid, context: self._get_default_address(cr, uid, 'city', context),
        'zip': lambda self, cr, uid, context: self._get_default_address(cr, uid, 'zip', context),
        'region': lambda self, cr, uid, context: self._get_default_address(cr, uid, 'region', context),
        'province': lambda self, cr, uid, context: self._get_default_address(cr, uid, 'province', context),
        'country_id': lambda self, cr, uid, context: self._get_default_address(cr, uid, 'country_id', context),
    }
    
    _sql_constraints = [('code_uniq', 'unique(code)', 'Code must be unique!')]

    def on_change_city(self, cr, uid, ids, city, zip_code=None):
        return self.pool.get('res.partner.address').on_change_city(cr, uid, ids, city, zip_code)
        
    def on_change_zip(self, cr, uid, ids, zip_code):
        return self.pool.get('res.partner.address').on_change_zip(cr, uid, ids, zip_code)

    def on_change_province(self, cr, uid, ids, province):
        return self.pool.get('res.partner.address').on_change_province(cr, uid, ids, province)

    def on_change_region(self, cr, uid, ids, region):
        return self.pool.get('res.partner.address').on_change_region(cr, uid, ids, region)

    def create(self, cr, uid, vals, context={}):
        if vals.get('code', '/') == '/':
            code = self.pool.get('ir.sequence').get(cr, uid, 'project.place')
            vals.update({'code': code})
        name = vals.get('code', '/')
        place_id = vals.get('place_id', False)
        parent_stock_id = False
        if place_id:
            place = self.pool.get('project.place').read(cr, uid, [place_id], context=context)[0]
            partner_id = place and place['partner_id'] and place['partner_id'][0] or False
            parent_stock_id = place and place['stock_location_id'] and place['stock_location_id'][0] or False
            if partner_id:
                vals.update({'partner_id': partner_id})
        vals.update({'name': name})
        
        res = super(project_plant, self).create(cr, uid, vals, context=context)
        if res:
            plant = self.read(cr, uid, [res], context=context)[0]
            stock_location = {
                'name': name,
                'usage': 'customer',
                'address_id': plant and plant['address_id'] and plant['address_id'][0] or False,
                'location_id': parent_stock_id or False
            }
            stock_location_id = self.pool.get('stock.location').create(cr, uid, stock_location, context=context)
            if stock_location_id:
                self.write(cr, uid, [res], {'stock_location_id': stock_location_id}, context=context)
        return res


class project_place(orm.Model):
    _name = "project.place"
    _inherits = {'res.partner.address': 'address_id'}
    
    def _get_plant_employees(self, cr, uid, ids, prop, unknow_none, context=None):
        if not len(ids):
            return {}
        res = []
        try:
            for place in self.browse(cr, uid, ids, context=context):
                employee_ids = []
                plant_ids = place.plant_ids
                for plant in self.pool[project.plant].browse(cr, uid, plant_ids, context=context):
                    for department in plant.plant_type_id.department_ids:
                        employee_ids += map(lambda e: e.id, department.member_ids)
                res.append((place.id, employee_ids))
        except:
            _logger.error('%s' % (repr(traceback.extract_tb(sys.exc_traceback))))
        return dict(res)
    
    def _get_moved_products_in(self, cr, uid, ids, prop, unknow_none, context=None):
        if not len(ids):
            return {}
        res = []
        try:
            for place in self.read(cr, uid, ids, ['stock_location_id']):
                if place['stock_location_id']:
                    res.append((place['id'], self.pool.get('stock.move').search(cr, uid, [('location_dest_id', '=', place['stock_location_id'][0])])))
        except:
            _logger.error('%s' % (repr(traceback.extract_tb(sys.exc_traceback))))
        return dict(res)
    
    def _get_moved_products_out(self, cr, uid, ids, prop, unknow_none, context=None):
        if not len(ids):
            return {}
        res = []
        try:
            for place in self.read(cr, uid, ids, ['stock_location_id']):
                if place['stock_location_id']:
                    res.append((place['id'], self.pool.get('stock.move').search(cr, uid, [('location_id', '=', place['stock_location_id'][0])])))
        except:
            _logger.error('%s' % (repr(traceback.extract_tb(sys.exc_traceback))))
        return dict(res)
    
 #   def _get_assigned_assets(self, cr, uid, ids, field_name, arg, context=None):
 #       return self.pool.get('asset.asset').get_current_assigned_assets(cr, uid, ids, field_name, self._name, context)
    
    _columns = {
        'address_id': fields.many2one('res.partner.address', "Address", required=True, ondelete='cascade'),
        'place_type_id': fields.many2one("project.place.type", "Place Type"),
        'place_type_need_more_info': fields.boolean("Need More Info"),
        'place_type_more': fields.char("More Info", size=24),
        'code': fields.char('Code', size=64),
        'project_ids': fields.many2many('project.project', 'project_project_project_place_rel', 'place_id', 'project_id', 'Projects', domain="[('partner_id', '=', partner_id)]"),
        'member_ids': fields.function(_get_plant_employees, method=True, string='Members', type='one2many', relation="hr.employee"),
        'stock_location_id': fields.many2one('stock.location', 'Stock Location', readonly=True),
        'stock_move_in_ids': fields.function(_get_moved_products_in, method=True, string='Products In', type='one2many', relation="stock.move"),
        'stock_move_out_ids': fields.function(_get_moved_products_out, method=True, string='Products Out', type='one2many', relation="stock.move"),
        'note': fields.text('Note'),
        #'asset_ids': fields.function(_get_assigned_assets, method=True, string='Assets', type='one2many', relation="asset.asset"),
        'plant_ids': fields.one2many('project.plant', 'place_id', 'Plants'),
    }
    
    _defaults = {
        'code': '/',  # lambda self, cr, uid, context: self.pool.get('ir.sequence').get(cr, uid, 'project.place'),
        'type': 'place',
    }
    
    _sql_constraints = [('code_uniq', 'unique(code)', 'Code must be unique!')]
    
    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
            
        if not args:
            args = []
        args = args[:]
        
        if args and len(args[0]) == 3 and args[0][1] == 'ilike':
            ## Ex: args = [('name', 'ilike', 'Q24M%nero')]
            args = [(args[0][0], 'ilike', args[0][2].replace(' ', '%'))]
        else:
            for i in range(len(args)):
                if args[i][0] == 'project_ids' and int(args[i][2]) > 0:
                    args[i] = ('project_ids', '=', self.pool.get('project.project').browse(cr, user, int(args[i][2]), context).name or '')
        
        return super(project_place, self).search(cr, user, args, offset=offset, limit=limit, order=order,
                                                 context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if args and len(args[0]) == 3 and args[0][1] == 'ilike':
            ## Ex: args = [('name', 'ilike', 'Q24M%nero')]
            args = [(args[0][0], 'ilike', args[0][2].replace(' ', '%'))]
        elif operator == 'ilike' and name:
            name = name.replace(' ', '%')
        return super(project_place, self).name_search(cr, user, name, args, operator, context, limit)
        
    def create(self, cr, uid, vals, context={}):
        #partner_id = vals.get('partner_id', False)
        #if partner_id:
        #    vals.update({'partner_id': partner_id})
        if vals.get('code', '/') == '/':
            vals['code'] = self.pool.get('ir.sequence').get(cr, uid, 'project.place')
            
        res = super(project_place, self).create(cr, uid, vals, context=context)
        if res:
            place = self.read(cr, uid, res, ['code', 'name', 'address_id'], context=context)
            location_name = "[%s] %s" % (place['code'], place['name'])
            stock_location = {
                'name': location_name,
                'usage': 'customer',
                'address_id': place and place['address_id'] and place['address_id'][0] or False,
            }
            stock_location_id = self.pool.get('stock.location').create(cr, uid, stock_location, context=context)
            if stock_location_id:
                self.write(cr, uid, [res], {'stock_location_id': stock_location_id}, context=context)
        return res
    
    def on_change_city(self, cr, uid, ids, city, zip_code=None):
        return self.pool.get('res.partner.address').on_change_city(cr, uid, ids, city, zip_code)
        
    def on_change_zip(self, cr, uid, ids, zip_code):
        return self.pool.get('res.partner.address').on_change_zip(cr, uid, ids, zip_code)
    
    def on_change_province(self, cr, uid, ids, province):
        return self.pool.get('res.partner.address').on_change_province(cr, uid, ids, province)
    
    def on_change_region(self, cr, uid, ids, region):
        return self.pool.get('res.partner.address').on_change_region(cr, uid, ids, region)

    def onchange_place_type_id(self, cr, uid, ids, place_type_id, context=None):
        place_type_need_more_info = False

        if place_type_id:
            place_type_obj = self.pool.get('project.place.type')
            type_of_place = place_type_obj.browse(cr, uid, place_type_id, context)
            if type_of_place and type_of_place.need_more_info:
                place_type_need_more_info = True
        return {'value': {'place_type_need_more_info': place_type_need_more_info}}


#class gallery_images(osv.osv):
#    _name = "web.gallery.images"
#    _inherit = "web.gallery.images"
#    _columns = {
#        'place_id': fields.many2one('project.place', "Place"),
#        'plant_id': fields.many2one('project.plant', "Plant"),
#    }
#gallery_images()
#
#
#class gallery_docs(osv.osv):
#    _inherit = "web.gallery.docs"
#    _columns = {
#        'place_id': fields.many2one('project.place', "Place"),
#        'plant_id': fields.many2one('project.plant', "Plant"),
#    }
#gallery_docs()


class plant_property(orm.Model):
    _name = 'plant.property'
    _description = 'Property'
      
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'group_id': fields.many2one('plant.property.group', 'Property Group', required=True),
        'description': fields.text('Description'),
        'plant_id': fields.many2one('project.plant', 'Plant'),
    }


class project_project(orm.Model):
    _inherit = 'project.project'
    _columns = {
        'location_ids': fields.many2many("project.place", "project_project_project_place_rel", "project_id", "place_id", "Locations", domain="[('partner_id', '=', partner_id)]"),
    }


class stock_move(orm.Model):
    _inherit = "stock.move"
    
    def _default_location_destination(self, cr, uid, context=None):
        """ Gets default address of partner for destination location
        @return: Address id or False
        """
        if context is None:
            context = {}
        if context.get('move_line', []):
            return super(stock_move, self)._default_location_destination(cr, uid, context=context)
        if context.get('address_out_id', False):
            address_id = context.get('address_out_id')
            address = self.pool['res.partner.address'].browse(cr, uid, context['address_out_id'], context=context)
            if address.type == 'plant':
                plant_ids = self.pool['project.plant'].search(cr, uid, [('address_id', '=', address_id)], context=context)
                if plant_ids:
                    plant = self.pool['project.plant'].browse(cr, uid, plant_ids, context=context)[0]
                    property_out = plant.stock_location_id and plantstock_location_id.id or False
                    return property_out
            if address.type == 'place':
                place_ids = self.pool['project.place'].search(cr, uid, [('address_id', '=', address_id)], context=context)
                if place_ids:
                    place = self.pool['project.place'].browse(cr, uid, place_ids, context=context)[0]
                    property_out = place.stock_location_id and place.stock_location_id.id or False
                    return property_out
            property_out = self.pool['res.partner.address'].browse(cr, uid, context['address_out_id'], context).partner_id.property_stock_customer
            return property_out and property_out.id or False
        return False
    
    _columns = {
        'invoice_state': fields.related('picking_id', 'invoice_state', type='char', size=16, string='Invoce Control', store=True, readonly=True)
    }
    
    _defaults = {
        'location_dest_id': _default_location_destination,
    }
