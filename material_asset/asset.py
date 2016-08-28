# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2012-2015 Didotech srl (info@didotech.com)
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
import datetime
from dateutil.relativedelta import relativedelta
import sys
import traceback
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def _get_locations(self, cr, uid, context=None):
    context = context or self.pool['res.users'].context_get(cr, uid)
    context['contact_display'] = 'partner_address'
    return self.pool['asset.location.property'].get_locations(cr, uid, context=context)


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


def get_relational_value(self, cr, uid, ids, field_name, arg, context=None):
    if not len(ids):
        return []
    value = {}
    context['contact_display'] = 'partner_address'
    for record in self.browse(cr, uid, ids, context):
        value[record.id] = record[arg['field_name']].name_get()[0][1]
    return value


def search_location(self, cr, uid, obj, name, args, context):
    if not args:
        return

    locations = []
    res = []

    model_search_field = {
        'asset.asset': {'field': 'name', 'field_name': 'location'},
        'asset.move': {'field_name': 'dest_location'},
        'project.project': {'query_start': """SELECT project_project.id FROM {model} LEFT JOIN account_analytic_account
            ON account_analytic_account.id = project_project.analytic_account_id """, 'field': 'name'},
        'res.partner': {'field': 'name'},
        'hr.employee': {'query_start': """SELECT hr_employee.id FROM {model} LEFT JOIN resource_resource
            ON resource_resource.id = hr_employee.resource_id """, 'field': 'name'},
        'res.partner.contact': {'field': 'name'},  # may be in the future we should add first_name also
        'stock.location': {'field': 'name'},
        'res.car': {'field': 'plate'},  # search car by the plate
        'project.place': {'query_start': """SELECT project_place.id FROM {model} LEFT JOIN res_partner_address
            ON res_partner_address.id = project_place.address_id """, 'field': 'res_partner_address.name'},
        'project.plant': {'query_start': """SELECT project_plant.id FROM {model} LEFT JOIN res_partner_address
            ON res_partner_address.id = project_plant.address_id """, 'field': 'res_partner_address.name'},
    }

    query_middle = "WHERE {model}.id = '{row_id}' AND "

    wanted_values = args[0][2].split(',')
    field_name = model_search_field[self._name]['field_name']

    cr.execute("""SELECT {field_name} FROM {table}
                    WHERE {field_name} IS NOT NULL
                    GROUP BY {field_name}""".format(table=self._name.replace('.', '_'), field_name=field_name))
    pretenders = cr.fetchall()
    pretenders = [p[0] for p in pretenders]

    for pretender in pretenders:
        model, row_id = pretender.split(',')
        if model in model_search_field.keys():
            if len(wanted_values) > 1:
                query_ends = ["{0} ILIKE '%{1}%'".format(model_search_field[model]['field'], v.strip()) for v in wanted_values]
                query_end = ' OR '.join(query_ends)
            else:
                query_end = "{0} ILIKE '%{1}%'".format(model_search_field[model]['field'], wanted_values[0].strip())

            if 'query_start' in model_search_field[model]:
                query_start = model_search_field[model]['query_start']
            else:
                query_start = "SELECT id FROM {model} "

            query = query_start.format(model=model.replace('.', '_')) + query_middle.format(model=model.replace('.', '_'), row_id=row_id) + query_end

            cr.execute(query)
            locations += ['{0},{1}'.format(model, r[0]) for r in cr.fetchall()]

    for location in locations:
        res += self.search(cr, uid, [(field_name, '=', '{location}'.format(location=location))], context=context)
    return [('id', 'in', res)]


class AssetLocationProperty(orm.Model):
    _name = 'asset.location.property'
    _description = 'All possible locations of an asset'

    _columns = {
        'name': fields.char(_('Name'), size=256, required=True, translable=True),
        'model': fields.char(_("Location model"), size=32, required=True),
        'location_field': fields.char(_("Fields"), size=32, required=False),
        'type': fields.selection(
            (
                ('address', 'Address'),
                ('location', 'Location'),
                ('other', 'Other')
            ),
            'Location Type',
            required=True
        ),
        'stock_location': fields.many2one('stock.location', 'Stock Location', required=False),
        'selectable': fields.boolean(_('Location is visible in selection menu'))
    }

    _defaults = {
        'selectable': True
    }

    _sql_constraints = [('model_uniq', 'unique(model)', 'Model must be unique!')]

    def get_locations(self, cr, uid, selectable_only=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        context['contact_display'] = 'partner_address'
        if selectable_only:
            domain = [('selectable', '=', True)]
        else:
            domain = []
        location_ids = self.search(cr, uid, domain, context=context)
        return [(l.model, l.name) for l in self.browse(cr, uid, location_ids, context)]

    def get_location(self, cr, uid, model, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        context['contact_display'] = 'partner_address'
        asset_location_ids = self.search(cr, uid, [('model', '=', model)], context=context)
        if asset_location_ids:
            return self.browse(cr, uid, asset_location_ids[0], context)
        else:
            return False


class asset_use(orm.Model):
    _description = "Asset Uses"
    _name = 'asset.use'

    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        for use in self.browse(cr, uid, ids, context):
            value[use.id] = use.color or 'black'
        return value

    _columns = {
        'name': fields.char("Use Type", size=256, required=True),
        'color': fields.selection(COLOR_SELECTION, 'Color'),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True,)
    }

    _order = "name"


class asset_category(orm.Model):

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id:
                name = record.parent_id.name + ' / ' + name
            res.append((record.id, name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _name = "asset.category"

    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'code': fields.char('Code', size=16, required=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
        'has_date_option': fields.boolean('Has date options ?'),
        'parent_id': fields.many2one('asset.category', 'Parent Category', select=True, ondelete='cascade'),
        'child_id': fields.one2many('asset.category', 'parent_id', string='Child Categories'),
        'asset_sequence_id': fields.many2one('ir.sequence', 'Asset sequence', domain=[('code', '=', 'asset.asset')]),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of product categories."),
        'asset_product_ids': fields.one2many('asset.product', 'asset_category_id', string=_('Asset Products'))
    }

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_left'
    
    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100

        while len(ids):
            cr.execute('select distinct parent_id from asset_category where id IN %s', (tuple(ids),))
            ids = filter(None, map(lambda x: x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You can not create recursive categories.', ['parent_id'])
    ]

    def child_get(self, cr, uid, ids):
        return [ids]
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        result = super(asset_category, self).name_search(cr, uid, name, args, operator, context, limit)
        print "Name: ", name
        if operator == 'ilike' and name:
            category_ids = self.search(cr, uid, [('name', 'ilike', name)], context=context)
            for category in self.browse(cr, uid, category_ids, context):
                result.append(category.name_get()[0])
        return list(set(result))

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        new_args = []
        
        for arg in args:
            if arg and len(arg) == 3 and arg[0] in ('parent_id', 'child_id') and arg[1] == '=':
                category_ids = super(asset_category, self).search(cr, uid, [arg], offset=offset, limit=limit, order=order, context=context, count=count)
                if category_ids:
                    new_category_ids = []
                    for category_id in category_ids:
                        new_category_ids += self.search(cr, uid, [(arg[0], '=', category_id)])
                    
                    new_args.append(('id', 'in', category_ids + new_category_ids))
                else:
                    new_args.append(arg)
            elif len(arg) == 3 and arg[0] == 'name' and arg[1] == 'ilike':
                category_ids = super(asset_category, self).search(cr, uid, [arg], offset=offset, limit=limit, order=order, context=context, count=count)
                if category_ids:
                    new_category_ids = []
                    for category_id in category_ids:
                        new_category_ids += self.search(cr, uid, [('parent_id', '=', category_id)])
                    
                    new_args.append(('id', 'in', category_ids + new_category_ids))
                else:
                    new_args.append(arg)
            else:
                new_args.append(arg)
    
        return super(asset_category, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)


class asset_image(orm.Model):
    _name = "asset.image"
    _column = {
        "asset_id": fields.many2one("asset.asset", "Asset"),
        "name": fields.char("Name", size=64),
        "file": fields.binary("Image"),
    }


class asset_product(orm.Model):
    _name = "asset.product"
    _inherits = {'product.product': 'product_product_id'}

    def _product_code(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = self._get_partner_code_name(cr, uid, [], p, context.get('partner_id', None), context=context)['code']
        return res

    _columns = {
        "user": fields.many2one("hr.employee", "Employee"),
        'inventory_code': fields.char("Numero di inventario", size=16),
        "asset_category_id": fields.many2one("asset.category", "Category", required=True),
        'has_date_option': fields.boolean('Has date options ?'),
        "asset_ids": fields.one2many('asset.asset', 'asset_product_id', string='Assets'),
    }

    def onchange_category_id(self, cr, uid, ids, asset_category_id, context=None):
        has_date_option = False
        if asset_category_id:
            category_id_obj = self.pool['asset.category']
            category_type = category_id_obj.browse(cr, uid, [asset_category_id], context)
            if category_type and category_type[0].has_date_option:
                has_date_option = True
        return {'value': {'has_date_option': has_date_option}}

    def _search_code(self, cr, uid, obj, name, args, context):
        code_ids = []

        # 'code': supinfo.product_code or product.default_code
        supplier_ids = self.pool.get('product.supplierinfo').search(cr, uid, [('product_code', 'ilike', args[2])], context=context)
        if supplier_ids:
            suppliers = self.pool.get('product.supplierinfo').browse(cr, uid, supplier_ids, context)
            for supplier in suppliers:
                code_ids += self.search(cr, uid, [('product_product_id', '=', supplier.product_id.id)], context=context)

        code_ids += self.search(cr, uid, [('default_code', 'ilike', args[2])], context=context)
        return [('id', 'in', code_ids)]

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        for k in range(0, len(args)):
            if args[k][0] == 'code':
                args[k] = self._search_code(cr, uid, 'obj', 'name', args[k], context)[0]

        return super(asset_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)


class asset_property_group(orm.Model):
    _name = 'asset.property.group'
    _description = 'Property Group'
    _columns = {
        'name': fields.char('Property Group', size=64, required=True),
        'description': fields.text('Description'),
    }


class account_asset_asset(orm.Model):
    _inherit = 'account.asset.asset'

    _columns = {
        'category_id': fields.many2one('account.asset.category', 'Asset category', change_default=True, readonly=True, states={'draft': [('readonly', False)]}),
    }

    _defaults = {
        'name': '/',
        'purchase_value': 0,
    }


class asset_asset(orm.Model):
    _name = "asset.asset"
    _description = 'Asset'

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return ()

        assets = self.browse(cr, uid, ids, context=context)
        res = []
        for asset in assets:
            name = ""
            if asset.name:
                name = "[" + asset.name + "] "
            if asset.asset_product_id:
                name = name + asset.asset_product_id.name

            if asset.serial_number:
                name = name + " (" + asset.serial_number.name + ")"
            res.append((asset.id, name))

        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def get_assigned_sims(self, cr, uid, ids, field_name, model_name, context=None):
        """
            This function show only assets that are assigned currently.
        """
        if not len(ids):
            return {}
        if not model_name:
            model_name = self._name

        res = {}
        sim_obj = self.pool['res.sim']

        # Get SIMs directly assigned to obj
        for obj_id in ids:
            res[obj_id] = sim_obj.search(cr, uid, [('location', '=', model_name + ',' + str(obj_id))], context=context)

        # Get SIMs assigned to assets assigned to parent obj
        assets = self.get_current_assigned_assets(cr, uid, ids, '', model_name, context)
        if assets:
            for obj_id in ids:
                for asset_id in assets[obj_id]:
                    res[obj_id] += sim_obj.search(cr, uid, [('location', '=', 'asset.asset,' + str(asset_id))], context=context)
        return res

    def get_all_assigned_sims(self, cr, uid, ids, field_name, arg, context=None):
        if not len(ids):
            return {}
        res = {}
        model_name = arg.get('model_name', self._name)
        start_date = arg.get('start_date', '1900-01-01 01:01:01')
        end_date = arg.get('end_date', datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT))

        for parent_id in ids:
            res[parent_id] = self.get_sim_movements(cr, uid, model_name, parent_id, start_date, end_date, context).keys()

        return res

    def get_sim_movements(self, cr, uid, model_name, parent_id, start_date, end_date, context=None):
        res = {}

        move_line_obj = self.pool['res.sim.move.line']

        # Get SIMs directly assigned to obj
        search_conditions = [
            ('dest_location', '=', model_name + ',' + str(parent_id)),
        ]
        move_line_ids = move_line_obj.search(cr, uid, search_conditions, order='datetime', context=context)
        sim_move_lines = move_line_obj.browse(cr, uid, move_line_ids, context)
        for move_line in sim_move_lines:
            if move_line.datetime < start_date:
                start = start_date
            else:
                start = move_line.datetime

            res[move_line.id] = {
                'sim_id': move_line.sim_id.id,
                'name': move_line.sim_id.complete_name,
                'added': start
            }

            search_conditions = [
                ('sim_id', '=', move_line.sim_id.id),
                ('source_location', '=', model_name + ',' + str(parent_id)),
                ('datetime', '>', start),
            ]
            return_line_ids = move_line_obj.search(cr, uid, search_conditions, order='datetime', context=context)
            if return_line_ids:
                return_line = move_line_obj.browse(cr, uid, return_line_ids[0], context)
                if return_line.datetime < end_date:
                    res[move_line.id]['returned'] = return_line.datetime
                else:
                    res[move_line.id]['returned'] = ''
            else:
                res[move_line.id]['returned'] = ''

        arg = {
            'model_name': model_name,
            'start_date': start_date,
            'end_date': end_date
        }

        # Get SIMs assigned to assets assigned to parent obj
        assigned_asset_moves = self.get_all_assigned_assets(cr, uid, [parent_id], 'sim_move_line_ids', arg, context)

        model_name = 'asset.asset'

        for asset_move_line_id in assigned_asset_moves[parent_id].keys():
            asset_move_line = assigned_asset_moves[parent_id][asset_move_line_id]
            search_conditions = [
                ('dest_location', '=', model_name + ',' + str(asset_move_line['asset_id'])),
            ]
            if asset_move_line['returned']:
                search_conditions.append(('datetime', '<=', asset_move_line['returned']))
            else:
                search_conditions.append(('datetime', '<=', end_date))
            print search_conditions
            print asset_move_line
            print

            # Search for Lines adding SIM to ASSET
            sim_move_line_ids = move_line_obj.search(cr, uid, search_conditions, order='datetime', context=context)

            if sim_move_line_ids:
                sim_move_lines = move_line_obj.browse(cr, uid, sim_move_line_ids, context)
                for move_line in sim_move_lines:
                    # move_line.datetime - date when sim was added to an asset
                    if move_line.datetime < start_date:
                        start = start_date
                    else:
                        start = move_line.datetime

                    # asset_move_line['added'] - date when asset was added.
                    if asset_move_line['added'] > start:
                        start = asset_move_line['added']

                    res[move_line.id] = {
                        'sim_id': move_line.sim_id.id,
                        'name': move_line.sim_id.complete_name,
                        'added': start,
                    }

                    search_conditions = [
                        ('sim_id', '=', move_line.sim_id.id),
                        ('source_location', '=', model_name + ',' + str(asset_move_line['asset_id'])),
                        ('datetime', '>', move_line.datetime),
                    ]
                    if asset_move_line['returned']:
                        search_conditions.append(('datetime', '<=', asset_move_line['returned']))
                    else:
                        search_conditions.append(('datetime', '<=', end_date))

                    return_line_ids = move_line_obj.search(cr, uid, search_conditions, order='datetime', context=context)
                    if return_line_ids:
                        return_line = move_line_obj.browse(cr, uid, return_line_ids[0], context)
                        if return_line.datetime < asset_move_line['added']:
                            del res[move_line.id]
                        elif return_line.datetime < end_date:
                            res[move_line.id]['returned'] = return_line.datetime
                        else:
                            if end_date < datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT):
                                res[move_line.id]['returned'] = end_date
                            else:
                                res[move_line.id]['returned'] = ''
                    else:
                        if asset_move_line['returned']:
                            res[move_line.id]['returned'] = asset_move_line['returned']
                        elif end_date < datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT):
                            res[move_line.id]['returned'] = end_date
                        else:
                            res[move_line.id]['returned'] = ''

        # Ex. res = {103: [342, 343, 344]}
        return res

    def get_all_assigned_assets(self, cr, uid, ids, field_name, arg, context=None):
        if not len(ids):
            return {}
        model_name = arg.get('model_name', self._name)
        start_date = arg.get('start_date', '1900-01-01 01:01:01')
        end_date = arg.get('end_date', datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT))

        res = {}
        movement = {}

        for parent_id in ids:
            movement[parent_id] = self.get_asset_movements(cr, uid, model_name, parent_id, start_date, end_date, context)
            res[parent_id] = movement[parent_id].keys()

        if field_name == 'sim_move_line_ids':
            return movement
        else:
            return res

    def get_asset_movements(self, cr, uid, model_name, parent_id, start_date, end_date, context=None):
        """
            Returns 'asset.move.line' objects for 'ids' locations
            @asset_id
            @location
            @start_date
            @end_date
        """

        move_line_obj = self.pool.get('asset.move.line')

        res = {}

        move_line_ids = move_line_obj.search(cr, uid, [
            ('dest_location', '=', model_name + ',' + str(parent_id)),
            ('date', '<=', end_date)
        ], order='date', context=context)
        move_lines = move_line_obj.browse(cr, uid, move_line_ids, context)
        for line in move_lines:
            if line.date > start_date:
                start = line.date
            else:
                start = start_date

            res[line.id] = {
                'asset_id': line.asset_id.id,
                'name': line.asset_id.complete_name,
                'location_id': line.dest_location.id,
                'model_name': line.dest_location._name,
                'added': start
            }
            return_ids = move_line_obj.search(cr, uid, [
                ('asset_id', '=', line.asset_id.id),
                ('source_location', '=', model_name + ',' + str(parent_id)),
                ('date', '>', line.date),
                ('date', '<=', end_date)
            ], order='date')

            if return_ids:
                return_line = move_line_obj.browse(cr, uid, return_ids[0], context)

                return_date_date = datetime.datetime.strptime(return_line.datetime, DEFAULT_SERVER_DATETIME_FORMAT)
                start_date_date = datetime.datetime.strptime(start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                if return_date_date > start_date_date:
                    if return_line.datetime < end_date:
                        res[line.id]['returned'] = return_line.datetime
                        new_end = return_line.datetime
                    else:
                        if end_date < datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT):
                            res[line.id]['returned'] = end_date
                        else:
                            res[line.id]['returned'] = ''
                        new_end = end_date

                    res[line.id]['location_id'] = return_line.dest_location.id
                    res[line.id]['model_name'] = return_line.dest_location._name
                else:
                    # Asset was removed before start_date
                    del res[line.id]
                    continue
            else:
                if end_date < datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT):
                    res[line.id]['returned'] = end_date
                else:
                    res[line.id]['returned'] = ''
                new_end = end_date

            # Check that asset is not inside itself
            if not line.asset_id.id == parent_id:
                movements = self.get_asset_movements(cr, uid, line.asset_id._name, line.asset_id.id, start, new_end)
                res.update(movements)

        return res

    def get_current_assigned_assets(self, cr, uid, ids, field_name, model_name, context=None):
        """
            This function show only assets that are assigned currently.
        """
        if not len(ids):
            return {}
        if not model_name:
            model_name = self._name
        res = {}

        for parent_id in ids:
            asset_ids = self.search(cr, uid, [('location', '=', model_name + ',' + str(parent_id))], context=context)
            tree = self.get_tree(cr, uid, asset_ids, context=context)
            res[parent_id] = [leave['ids'] for leave in tree]

        return res

    def get_asset_parents(self, cr, uid, ids, field_name, model_name, context=None):
        if not len(ids):
            return {}
        if not model_name:
            model_name = self._name
        res = {}

        objects = self.pool[model_name].browse(cr, uid, ids, context)
        for line in objects:
            if line.__hasattr__('location') and line.location and line == line.location:
                res[line.id] = ['Error: ', line.location.name_get()[0][1]]
            elif line.__hasattr__('location') and line.location:
                parent = self.get_asset_parents(cr, uid, [line.location.id], field_name, line.location._name)
                # Control if location is present in database:
                location_id = self.pool.get(line.location._name).search(cr, uid, [('id', '=', line.location.id)], context=context)
                if location_id and line.location.name_get():
                    res[line.id] = parent[line.location.id] + [line.location.name_get()[0][1]]
                else:
                    res[line.id] = parent[line.location.id] + ['Non existent location']
            else:
                res[line.id] = []

        return res

    def get_parents(self, cr, uid, ids, field_name, model_name, context=None):
        if not len(ids):
            return {}
        if not model_name:
            model_name = self._name
        res = {}

        parents = self.get_asset_parents(cr, uid, ids, field_name, model_name, context)
        for child_id in ids:
            if parents[child_id]:
                parents[child_id].pop(-1)

            if parents[child_id]:
                res[child_id] = ' / '.join(parents[child_id])
            else:
                res[child_id] = ''

        return res

    def _getPartner(self, cr, uid, ids, prop, unknown_none, context=None):
        if not len(ids):
            return []
        value = {}

        for record in self.browse(cr, uid, ids, context):
            if record.asset_product_id:
                product = self.pool['asset.product'].browse(cr, uid, record.asset_product_id.id, context)
                value[record.id] = product.manufacturer.name
        return value

    def _getKit(self, cr, uid, ids, prop, unknown_none, context=None):
        if not len(ids):
            return []
        value = {}
        for asset in self.browse(cr, uid, ids, context):
            if asset.asset_ids:
                value[asset.id] = True
        return value


    def _get_sim(self, cr, uid, ids, prop, unknown_none, context=None):
        if not len(ids):
            return []
        value = {}
        for asset in self.browse(cr, uid, ids, context):
            if asset.sim_ids:
                value[asset.id] = True
        return value

    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        assets = self.browse(cr, uid, ids, context)
        for asset in assets:
            if asset.asset_use_id:
                value[asset.id] = asset.asset_use_id.color
            else:
                value[asset.id] = 'black'

        return value

    def get_tree(self, cr, uid, ids, level=0, context=None):
        res = []
        context = context or self.pool['res.users'].context_get(cr, uid)
        for asset_id in ids:
            res.append({'ids': asset_id, 'level': level})
            children_ids = self.search(cr, uid, [('location', '=', 'asset.asset,' + str(asset_id))], context=context)
            if children_ids:
                # asset is inside itself
                if children_ids == ids:
                    return res
                # Stop crazy recursion
                if level > 400:
                    _logger.error('### Get_tree: Recursion too deep, children_ids = {0} ###'.format(str(children_ids)))
                    return res
                res += self.get_tree(cr, uid, children_ids, level + 1, context)
        return res

    def get_date(self, cr, uid, ids, field_name, arg, context=None):
        if not len(ids):
            return {}

        move_line_obj = self.pool['asset.move.line']
        res = {}

        for asset in self.browse(cr, uid, ids, context):
            asset_dest_line_ids = move_line_obj.search(cr, uid, [('asset_id', '=', asset.id), ('dest_location', '=', asset.location.id)], order='date desc', context=context)
            asset_source_line_ids = move_line_obj.search(cr, uid, [('asset_id', '=', asset.id), ('source_location', '=', asset.location.id)], order='date desc', context=context)
            if asset_dest_line_ids:
                asset_line = move_line_obj.browse(cr, uid, asset_dest_line_ids[0], context)
                res[asset.id] = {'added': asset_line.date}
                if asset_source_line_ids:
                    asset_line = move_line_obj.browse(cr, uid, asset_source_line_ids[0], context)
                    if asset_line.date > res[asset.id]['added']:
                        res[asset.id]['removed'] = asset_line.date
            else:
                res[asset.id] = {}

        return res

    def _get_sim_assets_change(self, cr, uid, ids, context=None):
        """
        This function works, because OpenERP make 3 passages here:
        before changing, after and in some other time. In some of this passages
        asset.location._name == 'asset.asset'.

        We should indicate explicitly 'asset.asset' and not self._name, because
        in this function we are inside 'res.sim' model.
        """
        asset_ids = []
        sim_obj = self.pool['res.sim']
        for sim in sim_obj.browse(cr, uid, ids, context=context):
            if sim.location and sim.location._name == 'asset.asset':
                asset_ids.append(sim.location.id)

        if asset_ids:
            assets = self.pool['asset.asset'].browse(cr, uid, asset_ids, context)
            for asset in assets:
                if asset.__hasattr__('location') and asset.location and asset.location._name == 'asset.asset':
                    parent_location_id = asset.location.id
                    asset_ids.append(asset.location.id)
                    while parent_location_id:
                        parent = self.pool['asset.asset'].browse(cr, uid, parent_location_id, context)
                        if parent.__hasattr__('location') and parent.location and parent.location._name == 'asset.asset':
                            parent_location_id = parent.location.id
                            asset_ids.append(parent.location.id)
                        else:
                            parent_location_id = False

        return asset_ids

    def _get_assets_assets_change(self, cr, uid, ids, context=None):
        asset_ids = []

        for asset in self.browse(cr, uid, ids, context=context):
            if asset.location and asset.location._name == self._name:
                asset_ids.append(asset.location.id)
        return asset_ids

    def _dummy_field(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        result = {}
        for asset_id in ids:
            result[asset_id] = ''
        return result

    def _get_stock_location(self, cr, uid, ids, field_name, args, context=None):
        move_obj = self.pool['stock.move']

        result = {}

        for asset in self.browse(cr, uid, ids, context):
            move_ids = move_obj.search(cr, uid, [('product_id', '=', asset.asset_product_id.product_product_id.id), ('prodlot_id', '=', asset.serial_number.id)], order='date desc', limit=1, context=context)
            if move_ids:
                move = move_obj.browse(cr, uid, move_ids[0], context)
                result[asset.id] = move.location_dest_id.id
            else:
                result[asset.id] = False

        return result

    _columns = {
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'asset_product_id': fields.many2one("asset.product", "Asset Product", required=True),
        'code': fields.related('asset_product_id', 'code', type='char', store=False, string=_('Product Code')),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
        'name': fields.char("Inventory Code", size=24, required=True),
        'serial_number': fields.many2one('stock.production.lot', "Serial Number", ondelete="no action", required=False),
        'new_serial_number': fields.function(_dummy_field, method=True, type="char", string='Serial Number'),
        'barcode': fields.char("Bar Code", size=16),
        'company_id': fields.many2one("res.company", "Company"),
        'partner_id': fields.function(_getPartner, method=True, type="char", string="Manufacturer"),
        'added': fields.function(get_date, method=True, type="datetime", multi=True, string="Added"),
        'removed': fields.function(get_date, method=True, type="datetime", multi=True, string="Removed"),
        'is_kit': fields.function(_getKit, method=True, type="boolean", string="Kit",
                                  store={
                                      'asset.asset': (_get_assets_assets_change, ['location'], 10),
                                  },
                                  ),
        'have_sim': fields.function(_get_sim, method=True, type="boolean", string="Sim",
                                    store={
                                        'res.sim': (_get_sim_assets_change, ['location'], 10),
                                        'asset.asset': (_get_assets_assets_change, ['location'], 10),
                                    },
                                    ),
        'ven_prod_name': fields.char("Vendor Product Name", size=64),
        'ven_prod_code': fields.char("Vendor Product code", size=64),
        'location': fields.reference("Current Location", _get_locations, size=128),
        'location_name': fields.function(get_relational_value, arg={'field_name': 'location'}, fnct_search=search_location, method=True, type="char", string="Current Location"),
        'stock_location_id': fields.function(_get_stock_location, "Current Stock Location", method=True, obj='stock.location', type='many2one'),
        'property_ids': fields.one2many('asset.property', 'asset_id', 'Properties'),
        'note': fields.text("Note"),
        'image': fields.binary("Image"),
        'date_start': fields.datetime("Starting Date"),
        'date_end': fields.datetime("Ending Date"),
        'has_date_option': fields.boolean('Has date options?'),
        'asset_use_id': fields.many2one('asset.use', 'Utilizzo'),
        'asset_ids': fields.function(get_current_assigned_assets, method=True, string='Assets', type='one2many', relation="asset.asset"),
        'asset_move_line_ids': fields.function(get_all_assigned_assets, arg={'model_name': 'asset.asset'}, method=True, string='Assets', type='one2many', relation="asset.move.line"),
        'asset_moves': fields.one2many('asset.move.line', 'asset_id', string='Asset Moves', readonly=True),
        'sim_ids': fields.function(get_assigned_sims, method=True, string='Sim', type='one2many', relation="res.sim"),
        'sim_move_line_ids': fields.function(get_all_assigned_sims, arg={'model_name': 'asset.asset'}, method=True, string='Assets', type='one2many', relation="res.sim.move.line"),
        'parents': fields.function(get_parents, method=True, string='Parents', type='char'),
        'active': fields.boolean('Active'),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True),
        'document_ids': fields.one2many("asset.document", 'asset_id', "Document"),
        'account_id': fields.many2one('account.analytic.account', 'Analytic Account', domain="[('type','!=','view'), ('parent_id', '!=', False)]"),
    }

    _sql_constraints = [
        ('track_number_uniq', 'unique(name)', 'Inventory code should be unique!'),
    ]

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'name': lambda self, cr, uid, context: self._get_sequence(cr, uid, False, context),
        'active': True,
        'date_start': lambda *a: datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    }

    def copy(self, cr, uid, id, default=None, context={}):
        inventory_code = self._get_sequence(cr, uid, False, context)

        if not default:
            default = {}
        default.update({
            'name': inventory_code,
        })
        return super(orm.Model, self).copy(cr, uid, id, default, context)

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []

        if name:
            name = name.lower()
            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
            if not ids:
                name = name.upper()
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)

        return self.name_get(cr, uid, ids, context=context)

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        new_args = []

        for arg in args:
            if arg and len(arg) == 3 and arg[1] == 'ilike':
                values = arg[2].split(',')
                if values > 1:
                    new_args += ['|' for x in range(len(values) - 1)] + [(arg[0], arg[1], value.strip()) for value in values]
            else:
                new_args.append(arg)

        return super(asset_asset, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)

    def write(self, cr, uid, ids, vals, context=None):
        if not ids:
            return False
        else:
            assets = self.browse(cr, uid, ids, context)

        if 'document_ids' in vals and len(vals['document_ids']) == 1:
            if 'document_type_id' in vals['document_ids'][0][2] and vals['document_ids'][0][2]['document_type_id'] and not vals['document_ids'][0][2]['active']:
                if vals['document_ids'][0][1]:
                    document_type = self.pool['asset.document.type'].browse(cr, uid, vals['document_ids'][0][2]['document_type_id'], context)
                    document = self.pool['asset.document'].browse(cr, uid, vals['document_ids'][0][1], context)
                    document_end_date = datetime.datetime.strptime(document.valid_end_date, DEFAULT_SERVER_DATE_FORMAT)
                    if document_type.repeatable and document_end_date <= datetime.datetime.now():
                        end_date = document_end_date + relativedelta(months=+document_type.duration)
                        new_document = {
                            'name': document.name,
                            'document_type_id': document_type.id,
                            'asset_id': document.asset_id.id,
                            'valid_start_date': document.valid_end_date,
                            'valid_end_date': end_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
                            'comments': document.comments,
                            'active': True,
                        }
                        self.pool['asset.document'].create(cr, uid, new_document, context)

        if 'new_serial_number' in vals and vals['new_serial_number'] and len(ids) == 1:
            prodlot_id = self.pool['stock.production.lot'].create(cr, uid, {
                'name': vals['new_serial_number'],
                'product_id': assets[0].asset_product_id.product_product_id.id,
            }, context)
            vals['serial_number'] = prodlot_id

        if 'location' in vals and vals['location'] and ',' not in vals['location']:
            del vals['location']
        return super(asset_asset, self).write(cr, uid, ids, vals, context)

    def _get_sequence(self, cr, uid, category_id, context=None):
        asset_category_obj = self.pool['asset.category']
        ir_sequence_obj = self.pool['ir.sequence']
        ir_model_data_obj = self.pool['ir.model.data']
        category = {}

        # Recursive search for a sequence on the category
        while category_id is not False:
            category = asset_category_obj.read(cr, uid, [category_id], ['asset_sequence_id', 'parent_id'], context=context)
            category = category and category[0] or {}
            # If the category has a sequence, stop here
            if category.get('asset_sequence_id', False):
                break

            # If the category has a parent, we continue on that parent, else, we stop
            category_id = category.get('parent_id', False)
            category_id = category_id and category_id[0] or False

        # If there is a sequence, we get its id
        if category.get('asset_sequence_id', False):
            res = ir_sequence_obj.get_id(cr, uid, category['asset_sequence_id'][0])

        # Else, we get the default asset sequence
        else:
            # Assert the default sequence exists (this can be deleted)
            model_data_id = ir_model_data_obj.search(cr, uid, [('module', '=', 'material_asset'), ('name', '=', 'seq_master_item')], context=context)
            if not model_data_id:
                return ""

            # Definition: get_object_reference(self, cr, uid, module, xml_id)
            # Strange enough: they call it xml_id, but it's name!
            sequence_data_id = ir_model_data_obj.get_object_reference(cr, uid, 'material_asset', 'seq_master_item')
            sequence_data_id = sequence_data_id and sequence_data_id[1]
            res = ir_sequence_obj.next_by_id(cr, uid, sequence_data_id)

        return res

    def create(self, cr, uid, values, context=None):
        asset_product_id = values.get('asset_product_id', False)
        if asset_product_id:
            asset_product = self.pool['asset.product'].browse(cr, uid, asset_product_id, context)
            category_id = asset_product.asset_category_id.id
            values['name'] = self._get_sequence(cr, uid, category_id)
            new_asset_id = super(asset_asset, self).create(cr, uid, values, context)
            message = _('An asset with Inventory code: {0} was created').format(values['name'])
            _logger.debug(message)
            self.log(cr, uid, new_asset_id, message)
            return new_asset_id
        else:
            raise orm.except_orm(_('Invalid action!'), _("You can't create an asset without a product"))

    def _check_dates(self, cr, uid, ids, context=None):
        for i in self.browse(cr, uid, ids, context=context):
            if i.has_date_option and i.date_start >= i.date_end:
                return False
        return True

    def _check_serial_unique(self, cr, uid, ids, context=None):
        result = True

        for asset in self.browse(cr, uid, ids, context):
            if asset.asset_product_id.lot_split_type == 'single':
                query = u"""SELECT stock_production_lot.name, asset_asset.asset_product_id, asset_asset.name
                FROM asset_asset
                INNER JOIN stock_production_lot ON asset_asset.serial_number=stock_production_lot.id
                WHERE asset_asset.asset_product_id={asset_product_id}
                AND stock_production_lot.name='{serial_number}'
                """.format(asset_product_id=asset.asset_product_id.id, serial_number=asset.serial_number.name)
                cr.execute(query)
                sql_result = cr.fetchall()

                if sql_result and not len(sql_result) == 1:
                    return False

        return result

    _constraints = [
        (_check_dates, _('Error! Documents start date must be lower then contract end date.'), ['has_date_option', 'date_start', 'date_end']),
        (_check_serial_unique, _('Duplicate asset serial number'), ['serial_number'])
    ]

    def _get_assets_serials(self, cr, uid, ids, product_id, context=None):
        stock_move_obj = self.pool['stock.move']
        serials = []

        asset_location_ids = self.pool['stock.location'].search(cr, uid, [('usage', '=', 'assets')], context=context)
        for location_id in asset_location_ids:
            stock_move_ids = stock_move_obj.search(cr, uid, [('location_dest_id', '=', location_id)], context=context)

            # TODO: order_by and only take serials that are still in location
            stock_move = stock_move_obj.browse(cr, uid, stock_move_ids, context)
            [serials.append(row.prodlot_id.name) for row in stock_move if not str(row.prodlot_id.name) == 'None']

        return serials

    def onchange_product_id(self, cr, uid, ids, asset_product_id, context=None):
        # TODO: We should show only non assigned serial numbers if product split type is Single
        has_date_option = False
        partner_id = ''
        product_product_id = 0
        if asset_product_id:
            asset_product_obj = self.pool['asset.product']
            asset_product = asset_product_obj.browse(cr, uid, asset_product_id, context)
            if asset_product and asset_product.has_date_option:
                has_date_option = True
            partner_id = asset_product.manufacturer.name
            product_product_id = asset_product.product_product_id.id

        assets_serials = self._get_assets_serials(cr, uid, ids, asset_product_id, context)

        return {
            'value': {'has_date_option': has_date_option, 'partner_id': partner_id},
            'domain': {'serial_number': [('product_id', '=', product_product_id), ('name', 'in', assets_serials)]},
        }

    def onchange_active(self, cr, uid, ids, active, context=None):
        if not active:
            now = datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            return {'value': {'date_end': now}}
        else:
            return {}

    def unlink(self, cr, uid, ids, context=None):
        if not self._check_serial_unique(cr, uid, ids, context):
            super(asset_asset, self).unlink(cr, uid, ids, context)
        else:
            raise orm.except_orm(_('Invalid action!'), _("Asset deletion is not permitted."))


class asset_property(orm.Model):
    _name = 'asset.property'
    _description = 'Property'

    def _get_property_location(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        res = {}
        properties = self.browse(cr, uid, ids, context)
        for asset_property in properties:
            res[asset_property.id] = asset_property.asset_id.location.name
        return res

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'group_id': fields.many2one('asset.property.group', 'Property Group', required=True),
        'description': fields.text('Description'),
        'asset_id': fields.many2one('asset.asset', 'Asset'),
        'location': fields.function(_get_property_location, method=True, type="char", fnct_search=search_location, string="Matching"),
    }

    def add(self, cr, uid, asset_id, name, description, group, group_description=''):
        '''
        @name: property value
        @group: Property name
        '''
        context = self.pool['res.users'].context_get(cr, uid)
        group_ids = self.pool['asset.property.group'].search(cr, uid, [('name', '=', group)], context=context)
        if group_ids:
            group_id = group_ids[0]
        else:
            group_id = self.pool['asset.property.group'].create(cr, uid, {'name': group, 'description': group_description}, context)

        return self.create(cr, uid, {'asset_id': asset_id, 'name': name, 'group_id': group_id, 'description': description}, context)


class resource_resource(orm.Model):
    _inherit = "resource.resource"
    _columns = {
        "asset_id": fields.many2one("asset.asset", "Asset"),
    }


class asset_move(orm.Model):
    _name = "asset.move"
    _inherits = {'stock.picking': 'stock_picking_id'}

    _columns = {
        "dest_location": fields.reference("Destination Location", _get_locations, size=128),
        'dest_location_name': fields.function(get_relational_value, arg={'field_name': 'dest_location'}, method=True, type="char", fnct_search=search_location, string="Destination Loc."),
        "user_id": fields.many2one("res.users", "Moved By", readonly=True),
    }

    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
    }

    # Seems it's impossible to order on inherited field...
    # _order = 'date_done desc'

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        # OpenERP don't like ordering on inherited field, so
        # to order on date_done we are using this trick.
        return super(asset_move, self).search(cr, uid, args, offset=offset, limit=limit, order='date_done desc', context=context, count=count)

    def create(self, cr, uid, vals, context=None):
        if len(vals) < 2:
            raise orm.except_orm(_('Warning!'), _("This is a wrong place for creating a move."))
        else:
            if 'date_done' in vals and len(vals['move_lines']) == 1:
                move_line_obj = self.pool['stock.move']
                move_lines = move_line_obj.browse(cr, uid, vals['move_lines'][0][2], context)
                for move_line in move_lines:
                    doubled_or_early_movements = move_line_obj.search(cr, uid, [('product_id', '=', move_line.product_id.id), ('prodlot_id', '=', move_line.prodlot_id.id), ('date', '>=', vals['date'])], context=context)
                    if len(doubled_or_early_movements) > 1 or (len(doubled_or_early_movements) == 1 and not doubled_or_early_movements[0] == move_line.id):
                        raise orm.except_orm(_('Warning!'), _("Product should be moved with the time superior to last move"))

            elif 'date_done' in vals and len(vals['stock_move_ids']) > 1:
                raise orm.except_orm(_('Error!'), _("Strange move. Please contact support"))
            elif 'date_done' in vals and len(vals['stock_move_ids']) < 1:
                raise orm.except_orm(_('Warning!'), _("You can't create empty move"))

            return super(asset_move, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        raise orm.except_orm(_('Warning!'), _("Asset Move can't be modified."))

    def unlink(self, cr, uid, ids, context=None):
        if len(ids) > 1:
            raise orm.except_orm(_('Error'), _('You can only delete one Asset Move at a time!'))
        else:
            move_line_obj = self.pool['stock.move']

            asset_move_to_delete = self.browse(cr, uid, ids[0], context)
            move_line_ids = move_line_obj.search(cr, uid, [('picking_id', '=', asset_move_to_delete.stock_picking_id.id)], context=context)
            
            for move_line in move_line_obj.browse(cr, uid, move_line_ids, context):
                # asset_id -> product_id + prodlot_id
                stock_move_ids = move_line_obj.search(cr, uid, [('product_id', '=', move_line.product_id.id), ('prodlot_id', '=', move_line.prodlot_id.id)], order='date_done desc', limit=1, context=context)
                
                if not stock_move_ids[0] == move_line.id:
                    raise orm.except_orm(_('Error'), _('You can only delete the last Asset Move!'))
                
                self.pool['asset.asset'].write(cr, uid, move_line.asset_id.id, {'location': '{0},{1}'.format(move_line.asset_source_location._name, move_line.asset_source_location.id)})

            move_line_obj.unlink(cr, uid, move_line_ids)
            self.pool['stock.picking'].unlink(cr, uid, [asset_move_to_delete.stock_picking_id.id], context)
            return super(asset_move, self).unlink(cr, uid, ids, context)

    def unlink2(self, cr, uid, ids, context=None):
        return super(asset_move, self).unlink(cr, uid, ids, context)


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _get_asset_from_product_serial(self, cr, uid, ids, field_name, args, context=None):
        result = {}

        for stock_move in self.browse(cr, uid, ids, context):
            asset_product_ids = self.pool['asset.product'].search(cr, uid, [('product_product_id', '=', stock_move.product_id.id)])
            if asset_product_ids:
                asset_ids = self.pool['asset.asset'].search(cr, uid, [('asset_product_id', '=', asset_product_ids[0]), ('serial_number', '=', stock_move.prodlot_id.id)])
                if asset_ids:
                    result[stock_move.id] = asset_ids[0]
                else:
                    result[stock_move.id] = False
            else:
                result[stock_move.id] = False
        
        return result
    
    def _get_asset_location(self, cr, uid, ids, field_names, args, context=None):
        result = {}
        
        field_mapping = {
            'asset_source_location': 'source_location'
        }
        
        asset_move_line_obj = self.pool['asset.move.line']

        asset_move_line_ids = asset_move_line_obj.search(cr, uid, [('stock_move_id', 'in', ids)], context=context)
        
        for asset_move_line in asset_move_line_obj.browse(cr, uid, asset_move_line_ids, context):
            result[asset_move_line.stock_move_id.id] = {}
            for field_name in field_names:
                result[asset_move_line.stock_move_id.id][field_name] = getattr(asset_move_line, field_mapping[field_name])
        
        moves_with_empty_location = set(ids) - set(asset_move_line_ids)
        for move_id in moves_with_empty_location:
            result[move_id] = {}
            for field_name in field_names:
                result[move_id][field_name] = False
        return result

    _columns = {
        'asset_id': fields.function(_get_asset_from_product_serial, obj='asset.asset', method=True, type='many2one'),
        'asset_source_location': fields.function(_get_asset_location, arg={'field_name': 'source_location'}, type='reference', method=True, multi=True),
    }


class asset_move_line(orm.Model):
    _name = 'asset.move.line'
    _inherits = {'stock.move': 'stock_move_id'}
    _description = 'Assets moved together'

    # def _get_return_datetime(self, cr, uid, ids, field_name, arg, context=None):
    #    '''
    #        This works only for 2 moves for the same location
    #    '''
    #
    #    if not len(ids):
    #        return {}
    #    res = []
    #    #pdb.set_trace()
    #    rows = self.browse(cr, uid, ids, context=context)
    #    for row in rows:
    #        ## TODO: rewrite
    #        #query = """SELECT source.asset_id, source.datetime, destination.datetime, source.dest_location
    #        #FROM asset_move_line AS source
    #        #LEFT JOIN asset_move_line as destination
    #        #ON source.asset_id=destination.asset_id
    #        #WHERE source.dest_location = destination.source_location
    #        #AND source.asset_id='{asset_id}'
    #        #AND source.datetime < destination.datetime
    #        #ORDER BY source.datetime""".format(asset_id=row.asset_id.id)
    #        #cr.execute(query)
    #        #result = cr.fetchall()
    #        #if result and result[0][2] > row.datetime:
    #        #    res.append((row.id, result[0][2]))
    #        #else:
    #        #    res.append((row.id, ''))
    #        res.append((row.id, ''))
    #
    #    return dict(res)

    def _getKit(self, cr, uid, ids, prop, unknown_none, context=None):
        res = {}
        asset_obj = self.pool['asset.asset']
        for asset_move_line in self.browse(cr, uid, ids, context):
            asset = asset_obj.browse(cr, uid, asset_move_line.asset_id.id, context)
            res[asset_move_line.id] = asset.is_kit

        return res

    _columns = {
        'source_location': fields.reference("Source Location", _get_locations, size=128),
        'dest_location': fields.reference("Destination Location", _get_locations, size=128),
        'user_id': fields.many2one("res.users", "Moved By", readonly=True),
        # 'source_location_name': fields.function(get_relational_value, arg={'field_name': 'source_location'}, method=True, type="char", string="Source Loc."),
        # 'dest_location_name': fields.function(get_relational_value, arg={'field_name': 'dest_location'}, method=True, type="char", string="Destination Loc."),
        'is_kit': fields.function(_getKit, method=True, type="boolean", string="Kit"),
        # 'return_datetime': fields.function(_get_return_datetime, method=True, type="datetime", string="Returned"),
    }


class hr_employee(orm.Model):
    _description = "Employee"
    _inherit = 'hr.employee'

    def _get_assigned_assets(self, cr, uid, ids, prop, unknow_none, context=None):
        if not len(ids):
            return {}
        model_name = super(hr_employee, self)._name
        res = []
        try:
            for id in ids:
                res.append((id, self.pool['asset.asset'].search(cr, uid, [('location', '=', model_name + ',' + str(id))], context=context)))
        except:
            print repr(traceback.extract_tb(sys.exc_traceback))
        return dict(res)

    _columns = {
        'asset_ids': fields.function(_get_assigned_assets, method=True, string='Assets', type='one2many', relation="asset.asset"),
    }


class res_car(orm.Model):
    _inherit = 'res.car'

    def _get_assigned_assets(self, cr, uid, ids, prop, unknow_none, context=None):
        if not len(ids):
            return {}
        model_name = super(res_car, self)._name
        res = []
        try:
            for id in ids:
                res.append((id, self.pool['asset.asset'].search(cr, uid, [('location', '=', model_name + ',' + str(id))])))
        except:
            print repr(traceback.extract_tb(sys.exc_traceback))
        return dict(res)

    _columns = {
        'asset_ids': fields.function(_get_assigned_assets, method=True, string='Assets', type='one2many', relation="asset.asset"),
    }


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def _get_assigned_assets(self, cr, uid, ids, prop, unknow_none, context=None):
        if not len(ids):
            return {}
        model_name = super(res_partner, self)._name
        res = []
        try:
            for id in ids:
                res.append((id, self.pool['asset.asset'].search(cr, uid, [('location', '=', model_name + ',' + str(id))])))
        except:
            print repr(traceback.extract_tb(sys.exc_traceback))
        return dict(res)

    _columns = {
        'asset_ids': fields.function(_get_assigned_assets, method=True, string='Assets', type='one2many', relation="asset.asset"),
    }


#class project_place(orm.Model):
#    _inherit = 'project.place'
#
#    def _get_assigned_assets(self, cr, uid, ids, prop, unknow_none, context=None):
#        if not len(ids):
#            return {}
#        model_name = super(project_place, self)._name
#        res = []
#        try:
#            for id in ids:
#                res.append((id, self.pool.get('asset.asset').search(cr, uid, [('location', '=', model_name + ',' + str(id))])))
#        except:
#            print repr(traceback.extract_tb(sys.exc_traceback))
#        return dict(res)
#
#    _columns = {
#        'asset_ids': fields.function(_get_assigned_assets, method=True, string='Assets', type='one2many', relation="asset.asset"),
#    }


class asset_document_type(orm.Model):
    _description = "Documents Types"
    _name = 'asset.document.type'

    def _check_date_option(self, cr, uid, ids, filed_name, arg, context):
        res = {}
        document_types = self.browse(cr, uid, ids, context)
        for document_type in document_types:
            if document_type.duration:
                res[document_type.id] = True
            else:
                res[document_type.id] = False
        return res

    _columns = {
        'name': fields.char("Document Type", size=256, required=True),
        'code': fields.char("Code", size=64),
        'has_date_option1': fields.function(_check_date_option, type='boolean', string='Has date options?', method=True),
        'duration': fields.integer("Month Duration"),
        'repeatable': fields.boolean('Repeatable?'),
    }

    def onchange_has_date_option1(self, cr, uid, ids, has_date_option1, context=None):
        val = False
        if has_date_option1:
            val = '0'
        return {'value': {'duration': val}}


class asset_document(orm.Model):
    _description = "Asset Document"
    _name = 'asset.document'

    def _check_date_option(self, cr, uid, ids, filed_name, arg, context):
        res = {}
        documents = self.browse(cr, uid, ids, context)
        for document in documents:
            if document.document_type_id.has_date_option1:
                res[document.id] = True
            else:
                res[document.id] = False
        return res

    def _check_if_expired(self, cr, uid, ids, filed_name, arg, context):
        res = {}
        documents = self.browse(cr, uid, ids, context)
        for document in documents:
            if document.valid_end_date and datetime.datetime.strptime(document.valid_end_date, DEFAULT_SERVER_DATE_FORMAT) < datetime.datetime.now():
                res[document.id] = True
            else:
                res[document.id] = False
        return res

    _columns = {
        'name': fields.char("Document", size=256, required=True),
        'document_type_id': fields.many2one('asset.document.type', 'Document Type'),
        'asset_id': fields.many2one('asset.asset', 'Asset', ondelete='cascade', required=True),
        'valid_start_date': fields.date("Valid Start Date"),
        'valid_end_date': fields.date("Valid End Date"),
        'comments': fields.text('Comments'),
        'has_date_option1': fields.function(_check_date_option, type='boolean', string='Has date options?', method=True),
        'expired': fields.function(_check_if_expired, type='boolean', string='Is it expired?', method=True),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': 1,
    }

    def _check_dates(self, cr, uid, ids, context=None):
        for i in self.browse(cr, uid, ids, context=context):
            if i.has_date_option1 and i.valid_start_date >= i.valid_end_date:
                return False
        return True

    _constraints = [(_check_dates, 'Error! Documents start date must be lower then contract end date.', ['has_date_option1', 'valid_start_date', 'valid_end_date'])]

    def onchange_document_type_id(self, cr, uid, ids, document_type_id, context=None):
        has_date_option1 = False
        if document_type_id:
            document_type_obj = self.pool['asset.document.type']
            document_type = document_type_obj.browse(cr, uid, [document_type_id], context)
            if document_type and document_type[0].has_date_option1:
                has_date_option1 = True
        return {'value': {'has_date_option1': has_date_option1}}

    def onchange_valid_start_date(self, cr, uid, ids, document_type_id, start_date, context=None):
        valid_end_date = False

        start = datetime.datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        if document_type_id:
            document_type_obj = self.pool['asset.document.type']
            document_type = document_type_obj.browse(cr, uid, document_type_id, context)
            if document_type and document_type.has_date_option1 and document_type.duration:
                valid_end_date = start + relativedelta(months=+document_type.duration)
                valid_end_date = valid_end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        return {'value': {'valid_end_date': valid_end_date}}
