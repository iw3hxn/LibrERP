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
from osv import fields, osv
import time
from tools.translate import _

#--
#--OpenERP Model class to manage Car Type
#--E.g. luxurious, economy, compact, intermediate, sports, minivan, Premium
#--
class res_car_type(osv.osv):
    _description = "Car Types"
    _name = 'res.car.type'
    _columns = {
        'name': fields.char("Name", size=256, required=True),
        'code': fields.char("Code", size=64),
    }
    _order = "name desc"
res_car_type()

#--
#--OpenERP Model to manage Car
#--
class res_car(osv.osv):
    _description = "Car"
    _name = 'res.car'
    _rec_name = 'plate'
    
    def _get_current_driver(self, cr, uid, ids, context, *a):
        res = {}
        date_start = time.strftime('%Y-%m-%d')
        for line in self.browse(cr, uid, ids):
            cr.execute( "select rs.employee_id from res_car_contract as rs  where state in ('draft', 'assigned') "\
                        " and ( rs.car_id = %s )"\
                        " and ( "\
                        "         rs.start_date <= %s and (rs.end_date is null or rs.end_date >= %s )  "\
                        " )", (line.id,date_start,date_start)
                       )
            employee = cr.fetchone()
            if employee:
                emps = self.pool.get('hr.employee').read(cr,uid,[employee[0]],['id','name'])
                obj = emps[0]
                res[line.id] = (obj['id'],obj['name'])
            else:
                res[line.id] = False
        return res
    
    _columns = {
        'plate': fields.char("Plate", size=256 , required=True),
        'fuel_card_number': fields.char("Fuel card number", size = 256),
        'car_type_id':fields.many2one('res.car.type','Type'),
        'telepass': fields.char("Telepass", size=256),
        'employee_id':fields.many2one('hr.employee','Employee',ondelete='cascade'),
        'documents_ids': fields.one2many('res.car.document', 'car_id', 'Documents'),
        'km_ids': fields.one2many('res.car.km', 'car_id', 'Km'),
        'telepass_ids': fields.one2many('res.telepass', 'car_id', 'Telepass'),
        'service_ids': fields.one2many('res.car.service', 'car_id', 'Servcies'),
        'contract_ids': fields.one2many('res.car.contract', 'car_id', 'Employee History'),
        'current_driver': fields.function(_get_current_driver, method=True, type='many2one', relation='hr.employee', string='Employee'),
        'note': fields.text('Note'),
        'is_available' : fields.boolean("Available"),
        #'lat': fields.char('Latitude', size = 22),
        #'lng': fields.char('Longitude', size = 22),
        #'map': fields.dummy(),
    }
    _defaults = {
        'is_available': 1,
    }

    _order = "plate desc"
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        return super(res_car, self).write(cr, uid, ids, vals, context=context)
    _sql_constraints = [
        ('plate_uniq', 'unique(plate)', 'Plate name must be unique !'),
    ]
res_car()



#--
#--OpenERP Model to manage Car Service Type
#--E.g. interim, full
#--
class res_car_service_type(osv.osv):
    _description = "Service Types"
    _name = 'res.car.service.type'
    _columns = {
        'name': fields.char("Service Type", size=256, required=True),
        'required_next_service': fields.boolean('Have next service ?'),
    }
    _order = "name"


#--
#--OpenERP Model to manage Car Service
#--
class res_car_service(osv.osv):
    _description = "Service"
    _name = 'res.car.service'
    _rec_name = 'service_date'
    _columns = {
        'service_date': fields.date("Date", required=True),
        'service_type_id':fields.many2one('res.car.service.type','Type'),
        'km':fields.integer('Km'),
        'next_service_km':fields.integer('Next service in km'),
        'car_id':fields.many2one('res.car','Car',ondelete='cascade'),
        'required_next_service': fields.boolean('Have next service ?'),
        'note':fields.text("Note"),
        'spent': fields.float('Spent'),
    }

  
    def _check_next_service_km(self, cr, uid, ids, context=None):
        for i in self.read(cr, uid, ids, ['required_next_service','next_service_km'], context=context):
            if i['required_next_service'] and not i['next_service_km']:
                return False
        return True

    _constraints = [(_check_next_service_km, 'Error! Please enter the next service Km.', ['required_next_service','next_service_km'])]

    def onchange_service_type_id(self, cr, uid, ids, service_type_id, context=None):
        required_next_service = False
        if service_type_id:
            service_type_obj = self.pool.get('res.car.service.type')
            service_type = service_type_obj.browse(cr,uid,[service_type_id],context)
            if service_type and service_type[0].required_next_service == True:required_next_service = True
        return {'value': {'required_next_service': required_next_service}}
res_car_service()

#--
#--OpenERP Model to manage Car fuel history
#--
class res_car_km(osv.osv):
    _description = "Km"
    _name = 'res.car.km'
    _rec_name = 'date'
    _columns = {
        'date': fields.date("Date", required=True),
        'km':fields.integer('Km'),
        'month_fuel_cost': fields.float('Monthly Fuel Cost', required=True),
        'car_id':fields.many2one('res.car','Car',ondelete='cascade'),
        'fuel_card_number': fields.related('car_id', 'fuel_card_number', string='Fuel Card Number', type='char', size=256, store=True),
        'note': fields.text('Note'),
    }
res_car_km()

class res_telepass(osv.osv):
    _description = "Telepass"
    _name = 'res.telepass'
    _rec_name = 'date'
    _columns = {
        'date': fields.date("Date", required=True),
        'spent':fields.float('Spent'),
        'car_id':fields.many2one('res.car','Car',ondelete='cascade'),
        'telepass': fields.related('car_id', 'telepass', string='Telepass', type='char', size=256, store=True),
        'note':fields.text('Note'),
    }
res_telepass()

class hr_employee(osv.osv):
    _description = "Employee"
    _inherit = 'hr.employee'
    _columns = {
        'car_id':fields.many2one('res.car','Car'),
        'contract_ids': fields.one2many('res.car.contract', 'employee_id', 'Car History'),
    }
hr_employee()

class res_car_contract(osv.osv):
    _description = "Contract"
    _name = 'res.car.contract'
    _rec_name = 'employee_id'
    _columns = {
        'employee_id':fields.many2one('hr.employee','Employee', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'car_id':fields.many2one('res.car','Car',ondelete='cascade', required=True , readonly=True, states={'draft':[('readonly',False)]}),
        'start_date': fields.date("Start Date" , required=True , readonly=True, states={'draft':[('readonly',False)]}),
        'end_date': fields.date("End Date" , readonly=True, states={'draft':[('readonly',False)]}),
        'state': fields.selection([('draft', 'Draft'),('assigned', 'Assigned'),('released', 'Released')], 'State', required=True, readonly=True),
        'isactive': fields.boolean('Active'),
    }

    _defaults = {
        'isactive': 1,
        'start_date': time.strftime('%Y-%m-%d'),
        'state': 'draft',
    }

    def _check_dates(self, cr, uid, ids, context=None):
        car = self.pool.get("res.car")
        employee = self.pool.get("hr.employee")
        contract = self.pool.get("res.car.contract")
        for i in self.read(cr, uid, ids, ['id','employee_id','car_id', 'start_date','end_date'], context=context):
            emp_id=i.get('employee_id',False)
            car_id=i.get('car_id',False)
            date_start =i.get('start_date',False)
            date_end =i.get('end_date', False) or '9999-12-31'
            cr.execute( "select * from res_car_contract where state in ('draft', 'assigned') "\
                        " and id != %s "\
                        " and ( employee_id = %s or car_id = %s )"\
                        " and ( "\
                        "        ( start_date <= %s and (end_date is null or end_date >= %s ))  "\
                        "        or ( start_date >= %s  and start_date <= %s)"\
                        " )", (i.get('id',0),emp_id[0],car_id[0],date_start,date_start,date_start,date_end)
                       )
            contract_ids = cr.fetchall()
            if len(contract_ids):
                return False
        return True
    _constraints = [(_check_dates, 'Error! Contract Start and End dates are not valid', ['employee_id','car_id', 'start_date','end_date'])]
    
    #def action_confirm(self, cr, uid, ids):
    #    self.write(cr, uid, ids, {'state':'confirmed'})
    #    return True

    def action_assigned(self, cr, uid, ids):
        for contract in self.read(cr,uid,ids):
            if contract['start_date'] == time.strftime('%Y-%m-%d'):
                self.write(cr, uid, [contract['id']], {'state':'assigned'})
                self.pool.get('res.car').write(cr,uid,[contract['car_id'][0]], {'employee_id':contract['employee_id'][0]})
                self.pool.get('hr.employee').write(cr,uid,[contract['employee_id'][0]], {'car_id':contract['car_id'][0]})
            else:
                raise osv.except_osv(_('Invalid Could Not Be Performed !'), _('Cannot assign Car which start date is different then current date!'))
        return True

    #def action_cancel(self, cr, uid, ids):
    #    self.write(cr, uid, ids, {'state':'cancel','end_date':time.strftime('%Y-%m-%d')})
    #    return True

    def action_released(self, cr, uid, ids):
        for contract in self.read(cr,uid,ids):
            self.write(cr, uid, [contract['id']], {'state':'released','end_date':time.strftime('%Y-%m-%d'),'isactive':False})
            self.pool.get('res.car').write(cr,uid,[contract['car_id'][0]], {'employee_id':False})
            self.pool.get('hr.employee').write(cr,uid,[contract['employee_id'][0]], {'car_id':False})
        #self.write(cr, uid, ids, {'state':'released','end_date':time.strftime('%Y-%m-%d')})
        return True

res_car_contract()





#class gallery_docs(osv.osv):
#    _inherit = "web.gallery.docs"
#    _columns = {
#        'car_document_id': fields.many2one('res.car.document', "Car Document")
#    }
#gallery_docs()
#
#class res_car_document1(osv.osv):
#    _inherit = "res.car.document"
#    _columns = {
#        # galleries
#        'web_gallery_doc_ids': fields.one2many('web.gallery.docs',
#                                   'car_document_id',
#                                   'Documents'),
#    }
#res_car_document1()
