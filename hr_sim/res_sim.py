# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Dhaval Patel (dhpatel82 at gmail.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from datetime import datetime
import re
import netsvc
LOGGER = netsvc.Logger()

import logging, traceback, sys
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


COLOR_SELECTION = [
         ('aqua', (u"Aqua")),
         ('black', (u"Black")),
         ('blue', (u"Blue")),
         ('brown', (u"Brown")),
         ('cadetblue', (u"Cadet Blue")),
         ('darkblue', (u"Dark Blue")),
         ('fuchsia', (u"Fuchsia")),
         ('forestgreen' , (u"Forest Green")),
         ('green', (u"Green")),
         ('grey', (u"Grey")),  
         ('red', (u"Red")),
         ('orange', (u"Orange"))
]


def get_relational_value(self, cr, uid, ids, field_name, arg, context=None):
    if not len(ids):
        return []
    res = []
    
    reads = self.read(cr, uid, ids, ['id', arg['field_name']], context=context)
    for record in reads:
        if record[arg['field_name']]:
            try:
                (model_name, obj_id) = record[arg['field_name']].split(',')
                if model_name and obj_id:
                    obj_id = int(obj_id)
                    model = self.pool.get(model_name)
                    model_obj = model.name_get(cr, uid, [obj_id])
                    if type(model_obj) == type([]):
                        obj_name = model_obj[0]
                    elif type(model_obj) == type({}):
                        obj_name = (obj_id, model_obj[obj_id])
                    else:
                        obj_name = ('', 'Unknown record type')
                        
                    if obj_name and len(obj_name) > 1 :
                        # print (record['id'], "[ " + model_name + " ] " + obj_name[1])
                        # res.append((record['id'], "[ " + model_name + " ] " + obj_name[1]))
                        res.append((record['id'], obj_name[1]))
                    else:
                        res.append((record['id'], ''))
                else:
                    res.append((record['id'], ''))
            except:
                _logger.error(repr(traceback.extract_tb(sys.exc_traceback)))
                res.append((record['id'], ''))
        else:
            res.append((record['id'], ''))
    return dict(res)


def search_location(self, cr, uid, obj, name, args, context):
    """
    Because of the limits of the internal search function sometimes
    we get strange results.
    For example, if we are looking for a location 'hr.employee,3',
    also 'hr.employee,35' will match. This happens because framework automatically
    adds % at the beginning and at the end of a word.
    
    """
    if not args:
        return
    
    locations = []
    res = []
    
    model_search_field = {
        'asset.asset': {'field': 'track_no', 'field_name': 'location'},
        'asset.move': {'field_name': 'dest_location'},
        'project.project': {'query_start': """SELECT project_project.id FROM {model} LEFT JOIN account_analytic_account 
            ON account_analytic_account.id = project_project.analytic_account_id """, 'field': 'name'},
        'res.sim': {'field_name': 'location'},
        'res.sim.allocation': {'field_name': 'dest_location'},
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
    pretenders = [p[0] for p in pretenders if p[0].strip()]
    
    for pretender in pretenders:
        model, row_id = pretender.split(',')
        if model in model_search_field.keys():
            if len(wanted_values) > 1:
                query_ends = ["{0} ILIKE '%{1}%'".format(model_search_field[model]['field'], v.strip()) for v in wanted_values]
                query_end = ' OR '.join(query_ends)
            else:
                query_end = "{0} ILIKE '%{1}%'".format(model_search_field[model]['field'], wanted_values[0].strip())
            
            if model_search_field[model].has_key('query_start'):
                query_start = model_search_field[model]['query_start']
            else:
                query_start = "SELECT id FROM {model} "
        
            query = query_start.format(model=model.replace('.', '_')) + query_middle.format(model=model.replace('.', '_'), row_id=row_id) + query_end
            
            if model == 'hr.employee':
                print query
            cr.execute(query)
            locations += ['{0},{1}'.format(model, r[0]) for r in cr.fetchall()]
    
    for location in locations:
        res += self.search(cr, uid, [(field_name, 'like', '{location}'.format(location=location))])
    return [('id', 'in', res)]


class res_sim_location(orm.Model):
    _name = "res.sim.location"
    _description = "Sim Reference Locations"
    _columns = {
        'name': fields.char('Name', size=60, required=True),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the sim allocation without removing it."),
        'model': fields.many2one('ir.model', 'Object', required=True),
    }
    _defaults = {
        'active' : lambda *a: True,
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'model' in vals:
            raise orm.except_orm(_('Error !'), _('You cannot modify the Object linked to the Document Type!\nCreate another Document instead !'))
        return super(res_sim_location, self).write(cr, uid, ids, vals, context=context)

def _get_location(self, cr, uid, context=None):
    cr.execute('SELECT m.model, s.name FROM res_sim_location s, ir_model m WHERE s.model = m.id ORDER BY s.name')
    return cr.fetchall()


class res_sim_subscription_type(orm.Model):
    _description = "Subscription Types"
    _name = 'res.sim.subscription.type'
    _columns = {
        'name': fields.char("Subscription Type", size=256, required=True),
        'code': fields.char("Code", size=64),
        'has_date_option': fields.boolean('Has date options ?'),
        'note': fields.text('Note'),
    }
    _order = "name"


class res_sim_type(orm.Model):
    _description = "Sim Types"
    _name = 'res.sim.type'
    _columns = {
        'name': fields.char("Subscription Type", size=256, required=True),
    }
    _order = "name"


class res_sim_use(orm.Model):
    _description = "Sim Uses"
    _name = 'res.sim.use'

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
        'name': fields.char("Use Type", size=256, required=True),
        'color': fields.selection(COLOR_SELECTION, 'Color'),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True,)
    }
    _order = "name"


class res_sim_apn_management_type(orm.Model):
    _description = "APN Management Type"
    _name = 'res.sim.apn.management.type'
    _columns = {
        'name': fields.char("APN Management Type", size=256, required=True),
    }
    _order = "name"


class res_sim_apn_group(orm.Model):
    _description = "APN Group"
    _name = 'res.sim.apn_group'
    _columns = {
        'name': fields.char("APN Group", size=256, required=True),
        'management_ids': fields.one2many('res.sim.apn.management', 'sim_apn_group_id', 'Group APN Management'),
    }
    _order = "name"


class res_sim_apn_management(orm.Model):
    _description = "Management Services APN"
    _name = 'res.sim.apn.management'
    _columns = {
        'number': fields.integer("N. Assigned"),
        'name': fields.many2one('res.sim.apn.management.type','APN Management Type'),
        'limit' : fields.integer("MB limit"),
        'warning' : fields.boolean("Warning"),
        'block' : fields.boolean("Block"),
        'sim_apn_group_id' : fields.many2one("res.sim.apn_group", "Group", required=True),
    }
    _order = "number"


class res_sim(orm.Model):
    _description = "Sim"
    _name = 'res.sim'

    def get_color(self, cr, uid, ids, field_name, arg, context=None):
        value = {}
        sims = self.browse(cr, uid, ids, context=context)
        for sim in sims:
            if sim.sim_use_id:
                value[sim.id] = sim.sim_use_id.color
            else:
                value[sim.id] = 'black'

        return value

    def _get_number(self, cr, uid, context):
        if context is None:
            context = {}
        res = self.pool['ir.sequence'].get(cr, uid, 'sim.card')
        return res

    def _check_with_employee(self, cr, uid, ids, prop, unknow_none, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['id', 'location'], context=context)
        res = []
        for record in reads:
            with_emp = False
            try:
                (model_name, obj_id) = record['location'] and record['location'].split(',') or [None,None]
                if model_name and model_name == 'hr.employee':
                    with_emp = True
            except:
                LOGGER.notifyChannel(self._name, netsvc.LOG_ERROR, repr(traceback.extract_tb(sys.exc_traceback)))
            res.append((record['id'], with_emp))
        return dict(res)
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        for sim in self.browse(cr, uid, ids, context):
            res.append((sim.id, '[' + sim.sim_internal_number + '] ' + sim.prefix_number + ' ' + sim.number))
        return res
    
    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)
    
    def get_united_field(self, cr, uid, ids, field_name, fields_to_unite, context=None):

        if not context:
            context = {}

        if not len(ids):
            return {}
        res = {}
        
        reads = self.read(cr, uid, ids, ['id'] + fields_to_unite, context=context)
        for record in reads:
            united_field = [record[field].strip() for field in fields_to_unite if record[field]]
            if united_field:
                res[record['id']] = ' '.join(united_field)
            else:
                res[record['id']] = ''
                
        return res
    
    def _get_parents(self, cr, uid, ids, field_name, model_name, context=None):
        if not len(ids):
            return {}
        return self.pool['asset.asset'].get_parents(cr, uid, ids, field_name, self._name, context)

    def _get_employee(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for sim in self.browse(cr, uid, ids, context=context):
            res[sim.id] = sim.with_employee and sim.location.id or False
        return res
    
    def _search_by_parent(self, cr, uid, obj, field_name, args, context=None):
        if not len(args) == 1:
            return []
        
        re_parent = re.compile(args[0][2], re.IGNORECASE)
        
        sim_ids = {}
        all_sim_ids = self.search(cr, uid, [], context=context)
        
        parents = self.pool['asset.asset'].get_asset_parents(cr, uid, all_sim_ids, field_name, 'res.sim', context)

        for child_id in all_sim_ids:
            if parents[child_id]:
                # remove direct matching:
                parents[child_id].pop(-1)
                
            if parents[child_id]:
                for parent in parents[child_id]:
                    if re_parent.search(parent):
                        sim_ids[child_id] = True
                        continue
        
        return [('id', 'in', sim_ids.keys())]
        
    _columns = {
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
        'not_available': fields.boolean("Not Available"),
        'imei': fields.char("ICCID Number", size=19, required=True),
        'sim_internal_number': fields.char('Number', size=32, help="Internal Number", required=True),
        'prefix_number': fields.char("Prefix Phone Number", size=4,required=True ),
        'number': fields.char("Phone Number", size=256, required=True),
        'main_number': fields.function(get_united_field, arg=['prefix_number', 'number'], method=True, type="char", string="Main number"),
        'prefix_fax_number': fields.char("Prefix Fax Number", size=4),
        'fax_number': fields.char("Fax Number", size=256),
        'united_fax_number': fields.function(get_united_field, arg=['prefix_fax_number', 'fax_number'], method=True, type="char", string="Fax number"),
        'prefix_data_number': fields.char("Prefix Data Number", size=4),
        'data_number': fields.char("Data Number", size=256),
        'united_data_number': fields.function(get_united_field, arg=['prefix_data_number', 'data_number'], method=True, type="char", string="Data number"),
        'pin': fields.char("Pin", size=4, required=True),
        'puk': fields.char("Puk", size=8, required=True),
        'subscription_type_id': fields.many2one('res.sim.subscription.type', 'Subscription Type'),
        'sim_type_id': fields.many2one('res.sim.type', 'Sim Type'), 
        'sim_use_id': fields.many2one('res.sim.use', 'Utilizzo'),
        'apn_group_id': fields.many2one('res.sim.apn_group', 'APN Group'), 
        # 'employee_id': fields.many2one('hr.employee', 'Employee', ondelete='cascade'),
        'employee_id': fields.function(_get_employee, method=True, string="Employee", type="many2one", relation="hr.employee"),
        'subscription_start_date': fields.date("Start Date"),
        'subscription_end_date': fields.date("End Date"),
        'note': fields.text('Note'),
        'has_date_option': fields.boolean('Has date options ?'),
        'default': fields.boolean('Default'),
        'data': fields.boolean('Data'),
        'voice': fields.boolean('Voice'),
        'payment_ids': fields.one2many('res.sim.payment', 'sim_id', 'Payment History'),
        'sim_moves': fields.one2many('res.sim.move.line', 'sim_id', string='Sim Moves', readonly=True),
        'location': fields.reference("Matching", selection=_get_location, size=128, readonly=True),
        'location_name': fields.function(get_relational_value, arg={'field_name': 'location'}, fnct_search=search_location, method=True, type="char", string="Matching"),
        'parents': fields.function(_get_parents, fnct_search=_search_by_parent, method=True, string='Parents', type='char'),
        'with_employee': fields.function(_check_with_employee, method=True, type="boolean", string="With Employee?"),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True,)
    }

    _defaults = {
        'sim_internal_number': _get_number,
        'default': 0,
        'data': 1,
        'voice': 1,
    }

    _sql_constraints = [
        ('imei_uniq', 'unique(imei)', 'ICCID Code must be unique !'),
        ('sim_internal_number', 'unique(sim_internal_number)', 'SIM Internal Code must be unique !'),
    ]

    _order = "prefix_number asc, number asc, prefix_fax_number asc, fax_number asc, prefix_data_number asc, data_number asc" 

    def set_default_phone(self, cr, uid, ids, context=None):
        for sim in self.browse(cr, uid, ids, context=context):
            if sim.employee_id:
                sim_ids = self.search(cr, uid, [('employee_id', '=', sim.employee_id.id)], context=context)
                self.pool['hr.employee'].write(cr, uid, [sim.employee_id.id], {'work_phone': sim.prefix_number + sim.number}, context=context)
                self.write(cr, uid, sim_ids, {'default': False}, context=context)
                self.write(cr, uid, [sim.id], {'default': True}, context=context)
        return True

    def _check_dates(self, cr, uid, ids, context=None):
        for i in self.read(cr, uid, ids, ['has_date_option', 'subscription_start_date', 'subscription_end_date'], context=context):
            if i['has_date_option'] and i['subscription_start_date'] >= i['subscription_end_date']:
                return False
        return True

    _constraints = [(_check_dates, 'Error! Subscription start date must be lower then contract end date.', ['subscription_start_date', 'subscription_end_date'])]  
    
    def onchange_subscription_type_id(self, cr, uid, ids, subscription_type_id, context=None):
        has_date_option = False
        if subscription_type_id:
            subscription_type_obj = self.pool['res.sim.subscription.type']
            subscription_type = subscription_type_obj.browse(cr, uid, [subscription_type_id], context)
            if subscription_type and subscription_type[0].has_date_option:
                has_date_option = True
        return {'value': {'has_date_option': has_date_option}}
        
    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        field_to_sql = {
            'prefix_number': "'{field}%'",
            'number': "'{field}%'",
            'prefix_fax_number': "'{field}%'",
            'fax_number': "'{field}%'",
            'prefix_data_number': "'{field}%'",
            'data_number': "'{field}%'",
            'sim_internal_number': "'{field}'"
        }
        
        query_arg = []
        for arg in args:
            if arg and len(arg) == 3 and arg[0] in field_to_sql.keys() and arg[1] == 'ilike':
                values = []
                field_values = arg[2].split(',')
                
                sql_values = ['{0} LIKE '.format(arg[0]) + field_to_sql[arg[0]].format(field=value.strip()) for value in field_values]
                
                if len(sql_values) > 1:
                    query_arg.append(' OR '.join(sql_values))
                else:
                    query_arg += sql_values
                
        if query_arg:
            if len(query_arg) > 1:
                query = ' AND '.join(query_arg)
            else:
                query = query_arg[0]
            
            query = "SELECT id FROM res_sim WHERE " + query

            cr.execute(query)
            res = [x[0] for x in cr.fetchall()]
            if res:
                return res
            else:
                return []
            
        return super(res_sim, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        # This is the right way, but requires rewriting of the search function:
        # sim_ids = self.search(cr, uid, ['|', '|', ('sim_internal_number', 'ilike', name), ('prefix_number', 'ilike', name), ('number', 'ilike', name)])
        sim_ids = self.search(cr, uid, [('sim_internal_number', 'ilike', name + '%')])
        sims = self.browse(cr, uid, sim_ids)
        res = [(sim.id, '[' + sim.sim_internal_number + '] ' + sim.prefix_number + ' ' + sim.number) for sim in sims]
        return res
        
    def write(self, cr, uid, ids, vals, context=None):
        if 'location' in vals and vals['location'] and not ',' in vals['location']:
            del vals['location']
        return super(res_sim, self).write(cr, uid, ids, vals, context)


class res_sim_traffic(orm.Model):
    _description = "Traffic information"
    _name = 'res.sim.traffic'
    
    _columns = {
        'sim_id': fields.many2one('res.sim', 'SIM'),
        'call_type': fields.char("Call Type", size=256),
        'description': fields.char("Description", size=256),
        'dest_number': fields.char("Phone number", size=24),
        'call_date': fields.datetime('Call Date'),
        'duration': fields.integer('Duration'),
        'data_packets': fields.integer('Duration'),
        'amount': fields.float('Amount'),
        'contract': fields.char("Internet Contract", size=256), 
    }


class res_sim_payment(orm.Model):
    _description = "Sim payment line"
    _name = 'res.sim.payment'
    _year = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    
    def _get_year_total(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        if not len(ids):
            return {}
        for payment in self.read(cr, uid, ids, ['id'] + self._year):
            total_year = payment.get('jan', 0)
            total_year += payment.get('feb', 0)
            total_year += payment.get('mar', 0)
            total_year += payment.get('apr', 0)
            total_year += payment.get('may', 0)
            total_year += payment.get('jun', 0)
            total_year += payment.get('jul', 0)
            total_year += payment.get('aug', 0)
            total_year += payment.get('sep', 0)
            total_year += payment.get('oct', 0)
            total_year += payment.get('nov', 0)
            total_year += payment.get('dec', 0)
            res[payment['id']] = total_year
        return res
    
    def _check_negative(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        if not len(ids):
            return {}
        
        for payment in self.read(cr, uid, ids, ['id', 'type', 'sum_of_year'] + self._year):
            # print payment
            # check =  payment.get('jan', 0) >= 0 and \
            #    payment.get('feb', 0) >= 0 and \
            #    payment.get('mar', 0) >= 0 and \
            #    payment.get('apr', 0) >= 0 and \
            #    payment.get('jun', 0) >= 0 and \
            #    payment.get('jul', 0) >= 0 and \
            #    payment.get('aug', 0) >= 0 and \
            #    payment.get('sep', 0) >= 0 and \
            #    payment.get('oct', 0) >= 0 and \
            #    payment.get('nov', 0) >= 0 and \
            #    payment.get('dec', 0) >= 0 and True or False
            
            if payment.get('type', 'customer') == 'sum':
                res[payment['id']] = payment.get('sum_of_year', 0) < 0
            else:
                res[payment['id']] = False
        
        return res
    
    def _check_payment(self, cr, uid, ids, context=None):
        for payment in self.read(cr, uid, ids, context=context):
            sim_id = payment['sim_id'] and payment['sim_id'][0] or 0
            sum_payment_ids = self.search(cr, uid, [('type', '=', 'sum'), ('year', '=', payment.get('year', datetime.now().year)), ('sim_id', '=', sim_id)], context=context)
            if len(sum_payment_ids) > 0:
                return False
        return True

    def _ref_calc(self, cr, uid, ids, field_names=None, arg=False, context=None):
        res = {}.fromkeys(ids, {})
        if not ids:
            return res,
        for pay in self.read(cr, uid, ids, ['type', 'year', 'sim_id'] + self._year, context=context):
            type = pay['type']
            year = pay['year']
            sim_id = pay['sim_id'][0]
            if type == "customer" and year > 0:
                supplier_payment_ids = self.search(cr, uid, [('type', '=', 'supplier'), ('year', '=', year), ('sim_id', '=', sim_id)])
                if supplier_payment_ids:
                    supplier_payment = self.read(cr, uid, supplier_payment_ids[0], context=context)
                    res[pay['id']].update({
                        'jan_supplier': supplier_payment['jan'] or 0,
                        'feb_supplier': supplier_payment['feb'] or 0,
                        'mar_supplier': supplier_payment['mar'] or 0,
                        'apr_supplier': supplier_payment['apr'] or 0,
                        'may_supplier': supplier_payment['may'] or 0,
                        'jun_supplier': supplier_payment['jun'] or 0,
                        'jul_supplier': supplier_payment['jul'] or 0,
                        'aug_supplier': supplier_payment['aug'] or 0,
                        'sep_supplier': supplier_payment['sep'] or 0,
                        'oct_supplier': supplier_payment['oct'] or 0,
                        'nov_supplier': supplier_payment['nov'] or 0,
                        'dec_supplier': supplier_payment['dec'] or 0,
                    })
                sum_payment_ids = self.search(cr, uid, [('type', '=', 'sum'), ('year', '=', year), ('sim_id', '=', sim_id)])
                if sum_payment_ids:
                    sum_payment = self.read(cr, uid, sum_payment_ids[0], context=context)
                    res[pay['id']].update({
                        'jan_sum': sum_payment['jan'] or 0.00,
                        'feb_sum': sum_payment['feb'] or 0.00,
                        'mar_sum': sum_payment['mar'] or 0.00,
                        'apr_sum': sum_payment['apr'] or 0.00,
                        'may_sum': sum_payment['may'] or 0.00,
                        'jun_sum': sum_payment['jun'] or 0.00,
                        'jul_sum': sum_payment['jul'] or 0.00,
                        'aug_sum': sum_payment['aug'] or 0.00,
                        'sep_sum': sum_payment['sep'] or 0.00,
                        'oct_sum': sum_payment['oct'] or 0.00,
                        'nov_sum': sum_payment['nov'] or 0.00,
                        'dec_sum': sum_payment['dec'] or 0.00,
                    })
        return res

    def _get_sim_type_id(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        result = {}
        
        payments = self.browse(cr, uid, ids, context)
        for p in payments:
            # result[p.id] = p.sim_id.sim_type_id.name
            result[p.id] = p.sim_id.sim_type_id.id
            
        return result

    def _search_sim_type(self, cr, uid, obj, name, args, context):
        if not len(args) == 1:
            return []
        
        query = """SELECT res_sim_payment.id, res_sim.sim_type_id FROM res_sim_payment
        INNER JOIN res_sim ON res_sim_payment.sim_id = res_sim.id
        WHERE res_sim.sim_type_id = {sim_type_id}
        """.format(sim_type_id=args[0][2])
        
        cr.execute(query)
        query_result = cr.fetchall()
        payment_ids = [row[0] for row in query_result]
        return [('id', 'in', payment_ids)]
    
    def get_sim_type_selction(self, cr, uid, context=None):
        result = []
        sim_type_ids = self.pool.get('res.sim.type').search(cr, uid, [])
        sim_types = self.pool.get('res.sim.type').browse(cr, uid, sim_type_ids)
        for sim_type in sim_types:
            result.append((sim_type.id, sim_type.name))
        return result

    _columns = {
        'payment_date': fields.date("Date", required=True),
        #'month': fields.selection([
        #    ('1', 'January'),
        #    ('2', 'February'),
        #    ('3', 'March'),
        #    ('4', 'April'),
        #    ('5', 'May'),
        #    ('6', 'June'),
        #    ('7', 'July'),
        #    ('8', 'August'),
        #    ('9', 'September'),
        #    ('10', 'October'),
        #    ('11', 'November'),
        #    ('12', 'December'),
        #    ], 'Month'),
        'year': fields.integer('Year', required=True ),
        'payment_amount': fields.float('Amount'),
        #'reinvoice_1': fields.float('Amount 1'),
        #'reinvoice_2': fields.float('Amount 2'),
        'sim_id': fields.many2one('res.sim', 'Sim', ondelete='cascade', required=True),
        'sim_type_id': fields.function(_get_sim_type_id, string='Tipo SIM', fnct_search=_search_sim_type, type="selection", selection=get_sim_type_selction, method=True),
        'contract_id': fields.many2one('res.sim.subscription.type', 'Contract'),
        
        'note': fields.text('Note'),
        'jan': fields.float(u'Jan'),
        'feb': fields.float(u'Feb'),
        'mar': fields.float(u'Mar'),
        'apr': fields.float(u'Apr'),
        'may': fields.float(u'May'),
        'jun': fields.float(u'Jun'),
        'jul': fields.float(u'Jul'),
        'aug': fields.float(u'Aug'),
        'sep': fields.float(u'Sep'),
        'oct': fields.float(u'Oct'),
        'nov': fields.float(u'Nov'),
        'dec': fields.float(u'Dec'),

        'jan_fattura': fields.char(u'Fattura Gen', size=32),
        'feb_fattura': fields.char(u'Fattura Feb', size=32),
        'mar_fattura': fields.char(u'Fattura Mar', size=32),
        'apr_fattura': fields.char(u'Fattura Apr', size=32),
        'may_fattura': fields.char(u'Fattura Mag', size=32),
        'jun_fattura': fields.char(u'Fattura Giu', size=32),
        'jul_fattura': fields.char(u'Fattura Lug', size=32),
        'aug_fattura': fields.char(u'Fattura Ago', size=32),
        'sep_fattura': fields.char(u'Fattura Set', size=32),
        'oct_fattura': fields.char(u'Fattura Ott', size=32),
        'nov_fattura': fields.char(u'Fattura Nov', size=32),
        'dec_fattura': fields.char(u'Fattura Dic', size=32),
        
        'jan_protocollo': fields.char(u'Protocollo Gen', size=32),
        'feb_protocollo': fields.char(u'Protocollo Feb', size=32),
        'mar_protocollo': fields.char(u'Protocollo Mar', size=32),
        'apr_protocollo': fields.char(u'Protocollo Apr', size=32),
        'may_protocollo': fields.char(u'Protocollo Mag', size=32),
        'jun_protocollo': fields.char(u'Protocollo Giu', size=32),
        'jul_protocollo': fields.char(u'Protocollo Lug', size=32),
        'aug_protocollo': fields.char(u'Protocollo Ago', size=32),
        'sep_protocollo': fields.char(u'Protocollo Set', size=32),
        'oct_protocollo': fields.char(u'Protocollo Ott', size=32),
        'nov_protocollo': fields.char(u'Protocollo Nov', size=32),
        'dec_protocollo': fields.char(u'Protocollo Dic', size=32),
 
        'type': fields.selection([('supplier', 'Supplier'), ('customer', 'Customer'), ('sum', 'Sum')], 'Type'),
        'sum_of_year': fields.function(_get_year_total, method=True, string="Sum of Years", type="float", store=True),
        #'have_lost': fields.function(_check_negative, method=True, string="Have Loss?", type="boolean", store=True),
        'have_lost': fields.function(_check_negative, method=True, string="Have Loss?", type="boolean"),
        
        'sequence': fields.float('Sequence'),
        'jan_supplier': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Supplier Gen',),
        'feb_supplier': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Supplier Feb',),
        'mar_supplier': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Supplier Mar',),
        'apr_supplier': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Supplier Apr',),
        'may_supplier': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Supplier Mag',),
        'jun_supplier': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Supplier Giu',),
        'jul_supplier': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Supplier Lug',),
        'aug_supplier': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Supplier Ago',),
        'sep_supplier': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Supplier Set',),
        'oct_supplier': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Supplier Ott',),
        'nov_supplier': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Supplier Nov',),
        'dec_supplier': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Supplier Dic',),
        
        'jan_sum': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Sum Gen',),
        'feb_sum': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Sum Feb',),
        'mar_sum': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Sum Mar',),
        'apr_sum': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Sum Apr',),
        'may_sum': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Sum Mag',),
        'jun_sum': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Sum Giu',),
        'jul_sum': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Sum Lug',),
        'aug_sum': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Sum Ago',),
        'sep_sum': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Sum Set',),
        'oct_sum': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Sum Ott',),
        'nov_sum': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Sum Nov',),
        'dec_sum': fields.function(_ref_calc, method=True, multi='user_ref', type='float', string=u'Sum Dic',),
    }

    _defaults = {
        'year': lambda * a: datetime.now().year,
        'sim_id': lambda self, cr, uid, context: context.get('default_sim_id' ,False) or False,
        # 'month': lambda * a: datetime.now().month,
        # 'payment_date': fields.date.context_today,
    }
    _order = 'year desc, sequence, id'
    
    def write(self, cr, uid, ids, vals, context=None):
        for payment in self.browse(cr, uid, ids, context=context):
            is_year_changed = vals.has_key('year') and vals.get('year', payment.year) != payment.year or False
            if payment.type == 'sum':
                if (vals.has_key('type') and vals.get('type','sum') != 'sum') or is_year_changed:
                    raise orm.except_orm(
                        _('Operation forbidden'),
                        _('You are not allowed to change type or year for type once it defined as sum.')
                    )
                return super(res_sim_payment, self).write(cr, uid, [payment.id], vals, context=context)
            else:
                #--check year changed ???
                #--if year changed, need to update sum row of old year sum
                if is_year_changed:
                    vals.update({'sequence': vals.get('year', payment.year and payment.type == 'customer' and payment.year + 0.25 or payment.year) })
                res = super(res_sim_payment, self).write(cr, uid, [payment.id], vals, context=context)
                type = vals.get('type', payment.type)
                year = vals.get('year', payment.year)
                sim_id = vals.get('sim_id', payment.sim_id.id)
                sum_payment_ids = self.search(cr, uid, [('type','=','sum'), ('year', '=', year), ('sim_id', '=', sim_id)], context=context)
                
                year_payments = self.search(cr, uid, [('type', '!=', 'sum'), ('year', '=', year), ('sim_id', '=', sim_id)], context=context)
                res = {'jan': 0, 'feb': 0, 'mar': 0, 'apr': 0, 'may': 0, 'jun': 0, 'jul': 0, 'aug': 0, 'sep': 0, 'oct': 0, 'nov': 0, 'dec': 0,}
                for pay_line in self.read(cr, uid, year_payments, ['id', 'type'] + self._year):
                    is_supplier = pay_line['type'] == 'supplier'
                    res['jan'] += is_supplier and - pay_line['jan'] or pay_line['jan']
                    res['feb'] += is_supplier and - pay_line['feb'] or pay_line['feb']
                    res['mar'] += is_supplier and - pay_line['mar'] or pay_line['mar']
                    res['apr'] += is_supplier and - pay_line['apr'] or pay_line['apr']
                    res['may'] += is_supplier and - pay_line['may'] or pay_line['may']
                    res['jun'] += is_supplier and - pay_line['jun'] or pay_line['jun']
                    res['jul'] += is_supplier and - pay_line['jul'] or pay_line['jul']
                    res['aug'] += is_supplier and - pay_line['aug'] or pay_line['aug']
                    res['sep'] += is_supplier and - pay_line['sep'] or pay_line['sep']
                    res['oct'] += is_supplier and - pay_line['oct'] or pay_line['oct']
                    res['nov'] += is_supplier and - pay_line['nov'] or pay_line['nov']
                    res['dec'] += is_supplier and - pay_line['dec'] or pay_line['dec']    
                if len(sum_payment_ids) :
                    self.write(cr, uid, sum_payment_ids, res, context=context)
                else:
                    res.update({'type': 'sum', 'year': year, 'sim_id': sim_id , 'sequence': year + 0.5})
                    self.create(cr, uid, res, context=context)
                
                if is_year_changed:
                    changed_year_sum_payment_ids = self.search(cr, uid, [('type', '=', 'sum'), ('year','=',payment.year), ('sim_id', '=', payment.sim_id.id)], context=context)
                    if len(changed_year_sum_payment_ids) > 0:
                        changed_year_payments = self.search(cr, uid, [('type', '!=', 'sum'), ('year', '=', payment.year), ('sim_id', '=', payment.sim_id.id)], context=context)
                        res = { 'jan': 0, 'feb': 0, 'mar': 0, 'apr': 0, 'may': 0, 'jun': 0, 'jul': 0, 'aug': 0, 'sep': 0, 'oct': 0, 'nov': 0, 'dec': 0,}
                        for pay_line in self.read(cr, uid, changed_year_payments, ['id', 'type'] + self._year):
                            is_supplier = pay_line['type'] == 'supplier'
                            res['jan'] += is_supplier and - pay_line['jan'] or pay_line['jan']
                            res['feb'] += is_supplier and - pay_line['feb'] or pay_line['feb']
                            res['mar'] += is_supplier and - pay_line['mar'] or pay_line['mar']
                            res['apr'] += is_supplier and - pay_line['apr'] or pay_line['apr']
                            res['may'] += is_supplier and - pay_line['may'] or pay_line['may']
                            res['jun'] += is_supplier and - pay_line['jun'] or pay_line['jun']
                            res['jul'] += is_supplier and - pay_line['jul'] or pay_line['jul']
                            res['aug'] += is_supplier and - pay_line['aug'] or pay_line['aug']
                            res['sep'] += is_supplier and - pay_line['sep'] or pay_line['sep']
                            res['oct'] += is_supplier and - pay_line['oct'] or pay_line['oct']
                            res['nov'] += is_supplier and - pay_line['nov'] or pay_line['nov']
                            res['dec'] += is_supplier and - pay_line['dec'] or pay_line['dec']
                        self.write(cr, uid, changed_year_sum_payment_ids, res, context=context)
        return True
                
    def create(self, cr, uid, vals, context=None):
        type = vals.get('type', 'customer')
        year = vals.get('year', datetime.now().year)
        sim_id = vals.get('sim_id', 0)
        if not sim_id:
            raise orm.except_orm(
                _('Operation forbidden'),
                _('You have not defined the sim for given payment line')
            )
        
        sum_payment_ids = self.search(cr, uid, [('type', '=', 'sum'), ('year', '=', year), ('sim_id', '=', sim_id)], context=context)
        if type == 'sum' and len(sum_payment_ids) > 0:
            raise orm.except_orm(
                _('Operation forbidden'),
                _('You can not add more then one record with type is sum for same year')
            )
        if type == 'sum' and not len(sum_payment_ids):
            vals.update({'sequence': year + 0.5})
            return super(res_sim_payment, self).create(cr, uid, vals, context=context)

        vals.update({'sequence': year and type == 'customer' and year + 0.25 or year })
        
        new_id = super(res_sim_payment,self).create(cr, uid, vals, context=context)
        year_payments = self.search(cr,uid,[('type', '!=', 'sum'), ('year', '=', year), ('sim_id', '=', sim_id)], context=context)
        res = {'jan': 0, 'feb': 0, 'mar': 0, 'apr': 0, 'may': 0, 'jun': 0, 'jul': 0, 'aug': 0, 'sep': 0, 'oct': 0, 'nov': 0, 'dec': 0,}
        for pay_line in self.read(cr, uid, year_payments, ['id', 'type'] + self._year):
            is_supplier = pay_line['type'] == 'supplier'
            res['jan'] += is_supplier and - pay_line['jan'] or pay_line['jan']
            res['feb'] += is_supplier and - pay_line['feb'] or pay_line['feb']
            res['mar'] += is_supplier and - pay_line['mar'] or pay_line['mar']
            res['apr'] += is_supplier and - pay_line['apr'] or pay_line['apr']
            res['may'] += is_supplier and - pay_line['may'] or pay_line['may']
            res['jun'] += is_supplier and - pay_line['jun'] or pay_line['jun']
            res['jul'] += is_supplier and - pay_line['jul'] or pay_line['jul']
            res['aug'] += is_supplier and - pay_line['aug'] or pay_line['aug']
            res['sep'] += is_supplier and - pay_line['sep'] or pay_line['sep']
            res['oct'] += is_supplier and - pay_line['oct'] or pay_line['oct']
            res['nov'] += is_supplier and - pay_line['nov'] or pay_line['nov']
            res['dec'] += is_supplier and - pay_line['dec'] or pay_line['dec']    
        if len(sum_payment_ids):
            self.write(cr, uid, sum_payment_ids, res, context=context)
        else:
            res.update({'type': 'sum', 'year': year, 'sim_id': sim_id })
            self.create(cr, uid, res, context=context)
        return new_id
        
    def unlink(self, cr, uid, ids, context=None):
        raise orm.except_orm(_('Error'), _('You can not remove a payment line !'))
 
    def onchange_year(self,cr, uid, ids, type, year, context):
        pass
    
    def onchange_type(self, cr, uid, ids, type, year, sim_id=None, context=None):
        res = {
            'jan': 0,
            'feb': 0,
            'mar': 0,
            'apr': 0,
            'may': 0,
            'jun': 0,
            'jul': 0,
            'aug': 0,
            'sep': 0,
            'oct': 0,
            'nov': 0,
            'dec': 0,
        }
        if type == 'sum' and year > 0:
            sum_payment_ids = self.search(cr, uid, [('type', '=', 'sum'), ('year', '=', year)], context=context)
            if len(sum_payment_ids) > 0:
                return {'warning': {'title': _('Warning'), 'message': _('You can not add more then one record with type is sum for same year')}}
            year_payments = self.search(cr, uid, [('type', '!=', 'sum'), ('year', '=', year)], context=context)
            for pay_line in self.read(cr, uid, year_payments, ['id', 'type'] + self._year):
                is_supplier = pay_line['type'] == 'supplier'
                res['jan'] += is_supplier and - pay_line['jan'] or pay_line['jan']
                res['feb'] += is_supplier and - pay_line['feb'] or pay_line['feb']
                res['mar'] += is_supplier and - pay_line['mar'] or pay_line['mar']
                res['apr'] += is_supplier and - pay_line['apr'] or pay_line['apr']
                res['may'] += is_supplier and - pay_line['may'] or pay_line['may']
                res['jun'] += is_supplier and - pay_line['jun'] or pay_line['jun']
                res['jul'] += is_supplier and - pay_line['jul'] or pay_line['jul']
                res['aug'] += is_supplier and - pay_line['aug'] or pay_line['aug']
                res['sep'] += is_supplier and - pay_line['sep'] or pay_line['sep']
                res['oct'] += is_supplier and - pay_line['oct'] or pay_line['oct']
                res['nov'] += is_supplier and - pay_line['nov'] or pay_line['nov']
                res['dec'] += is_supplier and - pay_line['dec'] or pay_line['dec']
            return {'value': res}
        if type=="customer" and year > 0:
            res = {}
            supplier_payment_ids = self.search(cr, uid, [('type','=','supplier'),('year','=',year),('sim_id','=',sim_id)])
            if supplier_payment_ids:
                supplier_payment = self.read(cr,uid,supplier_payment_ids[0],context=context)
                res.update({
                    'jan_supplier': supplier_payment['jan'] or 0,
                    'feb_supplier': supplier_payment['feb'] or 0,
                    'mar_supplier': supplier_payment['mar'] or 0,
                    'apr_supplier': supplier_payment['apr'] or 0,
                    'may_supplier': supplier_payment['may'] or 0,
                    'jun_supplier': supplier_payment['jun'] or 0,
                    'jul_supplier': supplier_payment['jul'] or 0,
                    'aug_supplier': supplier_payment['aug'] or 0,
                    'sep_supplier': supplier_payment['sep'] or 0,
                    'oct_supplier': supplier_payment['oct'] or 0,
                    'nov_supplier': supplier_payment['nov'] or 0,
                    'dec_supplier': supplier_payment['dec'] or 0,
                })
            sum_payment_ids = self.search(cr, uid, [('type','=','sum'),('year','=',year),('sim_id','=',sim_id)])
            if sum_payment_ids:
                sum_payment = self.read(cr,uid,sum_payment_ids[0],context=context)
                res.update({
                    'jan_sum': sum_payment['jan'] or 0,
                    'feb_sum': sum_payment['feb'] or 0,
                    'mar_sum': sum_payment['mar'] or 0,
                    'apr_sum': sum_payment['apr'] or 0,
                    'may_sum': sum_payment['may'] or 0,
                    'jun_sum': sum_payment['jun'] or 0,
                    'jul_sum': sum_payment['jul'] or 0,
                    'aug_sum': sum_payment['aug'] or 0,
                    'sep_sum': sum_payment['sep'] or 0,
                    'oct_sum': sum_payment['oct'] or 0,
                    'nov_sum': sum_payment['nov'] or 0,
                    'dec_sum': sum_payment['dec'] or 0,
                })
            return {'value': res}
        return {'value': {}}
    
    def reset(self, cr, uid, ids, context):
        '''
        ids - res_sim_payment
        '''
        
        values = {}
        
        if not len(ids) == 1:
            return True
        
        client_payment = self.read(cr, uid, ids[0])
        sim_id = client_payment['sim_id'][0]
        supplier_payment_ids = self.search(cr, uid, [('type', '=', 'supplier'), ('year', '=', client_payment['year']), ('sim_id', '=', sim_id)])
        if len(supplier_payment_ids) == 1:
            supplier_payment = self.read(cr, uid, supplier_payment_ids[0])
        else:
            raise orm.except_orm(_('Warning!'), _("Too many rows with supplier payment"))
            
        for month in self._year:
            #print month
            #print 'Client', client_payment[month]
            #print 'Fornitore', supplier_payment[month]
            #print
            if not supplier_payment[month] == client_payment[month] and not client_payment[month]:
                values[month] = supplier_payment[month]
                values[month + '_fattura'] = 'reset'
        
        if values:
            self.write(cr, uid, ids, values)
        
        return True


class hr_employee(orm.Model):
    _description = "Employee"
    _inherit = 'hr.employee'
    
    def _get_assigned_sims(self, cr, uid, ids, field_name, arg, context=None):
        return self.pool.get('asset.asset').get_assigned_sims(cr, uid, ids, field_name, self._name, context)
 
    _columns = {
        'sim_ids': fields.function(_get_assigned_sims, method=True, string='Sims', type='one2many', relation="res.sim"),
    }


class res_sim_allocation(orm.Model):
    _name = "res.sim.allocation"

    _columns = {
        "name": fields.char('Comment/Reason', size=64, required=True, translate=True),
        'sim_move_lines': fields.one2many('res.sim.move.line', 'move_id', 'SIM lines'),
        "dest_location": fields.reference("Destination Location", selection = _get_location, size=128, ),
        "datetime": fields.datetime("Datetime", required=True),
        "user_id": fields.many2one("res.users","Moved By", readonly=True),
        'dest_location_name': fields.function(get_relational_value, arg={'field_name': 'dest_location'}, fnct_search=search_location, method=True, type="char", string="Destination Loc."),
        'company_id': fields.many2one('res.company', 'Company', required=True, select=True),    
    }
    
    _defaults = {
        'datetime': lambda *args: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda self, cr, uid, context: uid,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.move', context=c), 
    }
    _order ="datetime desc"
    
    def create(self, cr, uid, vals, context=None):
        if len(vals) < 2:
            raise orm.except_orm(_('Warning!'), _("This is a wrong place for creating a move."))
        else:
            return super(res_sim_allocation, self).create(cr, uid, vals, context)
        
    def write(self, cr, uid, ids, vals, context=None):
        raise orm.except_orm(_('Warning!'), _("SIM Allocation can't be modified."))
    
    def unlink(self, cr, uid, ids, context=None):
        if len(ids) > 1:
            raise orm.except_orm(_('Error'), _('You can only delete one SIM Allocation at a time!'))
        else:
            move_line_obj = self.pool['res.sim.move.line']
            move_line_ids = move_line_obj.search(cr, uid, [('move_id', '=', ids[0])])
            move_lines = move_line_obj.browse(cr, uid, move_line_ids, context=context)
            for line in move_lines:
                sim_move_lines = move_line_obj.search(cr, uid, [('sim_id', '=', line.sim_id.id)], order='datetime desc')
                if not sim_move_lines[0] == line.id:
                    raise orm.except_orm(_('Error'), _('You can only delete the last SIM movement!'))
                
        move_line_ids = move_line_obj.search(cr, uid, [('move_id', '=', ids[0])])
        for move_line_id in move_line_ids:
            move_line = move_line_obj.read(cr, uid, move_line_id, ['sim_id', 'source_location'])
            self.pool.get('res.sim').write(cr, uid, move_line['sim_id'][0], {'location': move_line['source_location']})
            
        move_line_obj.unlink(cr, uid, move_line_ids)
        return super(res_sim_allocation, self).unlink(cr, uid, ids, context)


class res_sim_move_line(orm.Model):
    _name = 'res.sim.move.line'
    _description = "SIMs movement"
    
    def _get_return_datetime(self, cr, uid, ids, field_name, arg, context=None):
        '''
            This works only for 2 moves for the same location
        '''
        if not len(ids):
            return {}
        res = []
        
        rows = self.browse(cr, uid, ids, context=context)
        for row in rows:
            query ="""SELECT source.sim_id, source.datetime, destination.datetime, source.dest_location 
            FROM res_sim_move_line AS source
            LEFT JOIN res_sim_move_line as destination
            ON source.sim_id=destination.sim_id
            WHERE source.dest_location = destination.source_location
            AND source.sim_id='{sim_id}'
            AND source.datetime < destination.datetime
            ORDER BY source.datetime""".format(sim_id=row.sim_id.id)
            cr.execute(query)
            result = cr.fetchall()
            if result and result[0][2] > row.datetime:
                res.append((row.id, result[0][2]))
            else:
                res.append((row.id, ''))
        
        return dict(res)
    
    _columns = {
        "description": fields.char('Comment/Reason', size=64, required=True, translate=True),
        "sim_id": fields.many2one("res.sim", "Sim", required=True),
        'move_id': fields.many2one('res.sim.allocation', 'Move'),
        "source_location": fields.reference("Source Location", selection = _get_location, size=128),
        "dest_location": fields.reference("Destination Location", selection = _get_location, size=128),
        "datetime": fields.datetime("Datetime", required=True),
        'return_datetime': fields.function(_get_return_datetime, method=True, type="datetime", string="Returned"),
        "user_id": fields.many2one("res.users","Moved By", readonly=True),
        'source_location_name': fields.function(get_relational_value, arg={'field_name': 'source_location'}, method=True, type="char", string="Source Loc."),
        'dest_location_name': fields.function(get_relational_value, arg={'field_name': 'dest_location'}, method=True, type="char", string="Destination Loc."),
    }
    
    _defaults = {
        'datetime': lambda *args: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda self, cr, uid, context: uid,
    }
    _order ="datetime"


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
