# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2012 ASPerience SARL (<http://www.asperience.fr>).
#    Copyright (c) 2012-2014 didotech SRL (info at didotech.com)
#    All Rights Reserved
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

from osv import fields, osv


class inherit_account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    def _payment(self, cr, uid, ids, name, arg, context=None):
        voucher_line_obj = self.pool.get('account.voucher.line')
        invoice_obj = self.pool.get('account.invoice')
        order_obj = self.pool.get('sale.order')
        
        res = {}
        
        for voucher in self.browse(cr, uid, ids):
            result = False
            if voucher.state == 'posted' and voucher.line_ids:
                for voucher_line in voucher.line_ids:
                    if voucher_line.move_line_id.invoice:
                        inv_origin = voucher_line.move_line_id.invoice.origin
                        if inv_origin:                        
                            order_ids = order_obj.search(cr, uid, [('name', '=', inv_origin)])
                            orders = order_obj.read(cr, uid, order_ids, ['invoiced', 'state'], context=context)
                            for order in orders:
                                if order['state'] in ['progress', 'done']:
                                    if order['invoiced']:
                                        order_obj.write(cr, uid, [order['id']], {'flag_paid': True}, context=context)
            res[voucher.id] = result
        
        return res

    _columns = {
        'flag_payment': fields.function(_payment, string='Payment', method=True, type='boolean'),
    }


class inherit_res_users(osv.osv):
    _inherit = 'res.users'
    
    def _is_agent(self, cr, uid, ids, name, arg, context=None):
        print ''
        resource_obj = self.pool.get('resource.resource')
        employee_obj = self.pool.get('hr.employee')

        result = False
        res = {}
        resources = []
        resource_ids = resource_obj.search(cr, uid, [('user_id', '=', ids[0])])
        if resource_ids not in (False, [], 0, None, ''):
            resource_datas = resource_obj.read(cr, uid, resource_ids, ['id'], context=context)
            resources = resource_datas
        for resource in resources:
            employee_id = employee_obj.search(cr, uid, [('resource_id', '=', resource['id'])])
            if employee_id not in (False, [], 0, None, ''):
                employee_datas = employee_obj.read(cr, uid, employee_id, ['is_agent'], context=context)
                result = employee_datas[0]['is_agent']
                if result:
                    break
        res[ids[0]] = result
        return res
    
    _columns = {
        'is_agent': fields.function(_is_agent, string='Is agent', method=True, type='boolean'),
    }


class inherit_res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'agent_id': fields.many2one('hr.job', 'Agent', ondelete='cascade'),
        'area_manager_id': fields.many2one('hr.job', 'Area Manager', ondelete='cascade'),
    }


class inherit_sale_order(osv.osv):
    _inherit = 'sale.order'

    def _paying(self, cr, uid, ids, name, arg, context=None):
        result = False
        res = {}
        for data in self.read(cr, uid, ids, ['invoiced', 'state'], context=context):
            if data['state'] in ['progress', 'done']:
                if data['invoiced']:
                    result = True
        res[ids[0]] = result
        return res

    def _trimester(self, cr, uid, ids, name, arg, context=None):
        res = {}
        result = 0
        for data in self.read(cr, uid, ids, ['date_order'], context=context):
            if data['date_order'] not in (False, [], 0, None, ''):
                month = int(data['date_order'][5:7])
                if month in (1, 2, 3):
                    result = 1
                elif month in (4, 5, 6):
                    result = 2
                elif month in (7, 8, 9):
                    result = 3
                elif month in (10, 11, 12):
                    result = 4
                else:
                    result = 0
        res[ids[0]] = result
        return res

    def _is_area_manager(self, cr, uid, ids, name, arg, context=None):
        res = {}
        
        user = self.pool.get('res.users').browse(cr, uid, uid)
        area_manager_id = user.company_id.area_manager_id
        user_group_ids = [group.id for group in user.groups_id]
        manager_group_ids = self.pool.get('res.groups').search(cr, uid, [('name', '=', 'Agent / Manager')])
        
        if set(user_group_ids).intersection(manager_group_ids):
            result = True
        else:
            employee_obj = self.pool.get('hr.employee')
            resource_ids = self.pool.get('resource.resource').search(cr, uid, [('user_id', '=', uid)])
            employee_ids = employee_obj.search(cr, uid, [('resource_id', 'in', resource_ids)])
            employees = employee_obj.browse(cr, uid, employee_ids)
            
            if area_manager_id in [employee.job_id.id for employee in employees]:
                result = True
            else:
                result = False
         
        for order_id in ids:
            res[order_id] = result
        return res

    def _agent_commission(self, cr, uid, ids, name, arg, context=None):
        employee_obj = self.pool.get('hr.employee')
        lines_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        commission_obj = self.pool.get('hr.agent.commission')
        result = float(0.0)
        res = {}
        data_employees = {}
        for order in self.read(cr, uid, ids, ['internal_user_id', 'order_line', 'partner_id'], context=context):
            if order['internal_user_id'] in (False, [], 0, None, ''):
                res[ids[0]] = 0.0
                return res
            else:
                employees_ids = employee_obj.search(cr, uid, [('user_id', '=', order['internal_user_id'][0])])
                if employees_ids in (False, [], 0, None, ''):
                    res[ids[0]] = 0.0
                    return res
                else:
                    data_employees = employee_obj.read(cr, uid, employees_ids[0], ['hr_agent_commission_ids'], context=context)
            if order['order_line'] in (False, [], 0, None, ''):
                res[ids[0]] = 0.0
                return res
            else:
                datas_commission = commission_obj.read(cr, uid, data_employees['hr_agent_commission_ids'], ['product_id', 'category_id', 'customer_id', 'commission_percent', 'fixed_commission'], context=context)
                commission = 0.0
                value_line = 0.0
                for line in order['order_line']:
                    data_line = lines_obj.read(cr, uid, line, ['product_id', 'price_subtotal', 'discount', 'product_uom_qty'], context=context)
                    product_line = product_obj.read(cr, uid, data_line['product_id'][0], ['categ_id'], context=context)
                    value_line = data_line['price_subtotal']
                    if datas_commission not in (False, [], 0, None, ''):
                        find = False
                        # search for product
                        for data_commission in datas_commission:
                            if data_commission['product_id'] == data_line['product_id']:
                                find = True
                                commission = (value_line * data_commission['commission_percent'] / 100) + (data_commission['fixed_commission'] * data_line['product_uom_qty'])
                                break
                        # search for category product
                        if not find:
                            for data_commission in datas_commission:
                                if (data_commission['category_id'] not in (False, [], 0, None, '')) and (data_commission['category_id'][1] in product_line['categ_id'][1]):
                                    find = True
                                    commission = (value_line * data_commission['commission_percent'] / 100) + (data_commission['fixed_commission'] * data_line['product_uom_qty'])
                                    break
                        # search for customer
                        if not find:
                            for data_commission in datas_commission:
                                if data_commission['customer_id'] == order['partner_id']:
                                    find = True
                                    commission = (value_line * data_commission['commission_percent'] / 100) + (data_commission['fixed_commission'] * data_line['product_uom_qty'])
                                    break
                        #not find commissions
                        if not find:
                            commission = 0.0
                    result = result + commission
            res[ids[0]] = result
        return res

    def _area_manager_commission(self, cr, uid, ids, name, arg, context=None):
        employee_obj = self.pool.get('hr.employee')
        area_manager_commission_obj = self.pool.get('hr.area.manager.commission')
        lines_obj = self.pool.get('sale.order.line')
        result = float(0.0)
        res = {}
        data_area_manager_commission = {}
        for order in self.read(cr, uid, ids, ['internal_user_id', 'order_line', 'partner_id'], context=context):
            if order['internal_user_id'] and order['order_line']:
                employee_ids = employee_obj.search(cr, uid, [('user_id', '=', order['internal_user_id'][0])])
                if employee_ids:
                    data_employees = employee_obj.read(cr, uid, employee_ids[0], ['area_manager_id'], context=context)
                    if data_employees['area_manager_id']:
                        data_area_manager = employee_obj.read(cr, uid, data_employees['area_manager_id'][0], ['hr_area_manager_commission_ids'], context=context)
                        if data_area_manager['hr_area_manager_commission_ids']:
                            area_manager_commission_ids = area_manager_commission_obj.search(cr, uid, [('id', 'in', data_area_manager['hr_area_manager_commission_ids']), ('agent_id', '=', data_employees['id'])])
                            data_area_manager_commission = area_manager_commission_obj.read(cr, uid, area_manager_commission_ids, ['commission_percent', 'from_revenues', 'to_revenues'], context=context)
                        
                            value_total = 0.0
                            for line in order['order_line']:
                                value_line = 0.0
                                data_line = lines_obj.read(cr, uid, line, ['product_id', 'price_subtotal', 'discount', 'product_uom_qty'], context=context)
                                value_line = data_line['price_subtotal']
                                value_total = value_total + value_line
                            perc_commission = 0.0
                            for commission_area_manager in data_area_manager_commission:
                                if (value_total >= commission_area_manager['from_revenues']) and (value_total <= commission_area_manager['to_revenues']):
                                    perc_commission = commission_area_manager['commission_percent']
                            if perc_commission != 0:
                                result = value_total * perc_commission / 100
            res[order['id']] = result

        return res

    _columns = {
        'is_area_manager': fields.function(_is_area_manager, method=True, string='is Area Manager?', type='boolean'),
        'internal_user_id': fields.many2one('res.users', 'Agent', ondelete='cascade'),
        'trimester': fields.function(_trimester, method=True, store=True, string="Order's Trimester", type='integer'),
        'flag_paid': fields.function(_paying, string='Paid', method=True, store=True, type='boolean'),
        'sale_commission_amount': fields.function(_agent_commission, method=True, store=True, string="agent's commission", type='float'),
        'area_manager_commission': fields.function(_area_manager_commission, method=True, store=True, string="Area Manager's commission", type='float'),
    }
    _defaults = {
        'internal_user_id': lambda obj, cr, uid, context: uid,
    }


class hr_employee(osv.osv):
    _name = "hr.employee"
    _inherit = "hr.employee"

    def _manager_description(self, cr, uid, ids, name, arg, context=None):
        company_obj = self.pool.get('res.company')
        res = {}
        for company in self.read(cr, uid, ids, ['company_id', 'job_id'], context=context):
            datas = company_obj.read(cr, uid, company['company_id'][0], ['area_manager_id'], context=context)
            if datas['area_manager_id']:
                res[ids[0]] = datas['area_manager_id'][0]
        return res

    def _job_agent(self, cr, uid, ids, name, arg, context=None):
        company_obj = self.pool.get('res.company')
        res = {}
        result = False
        for company in self.read(cr, uid, ids, ['company_id', 'job_id'], context=context):
            datas = company_obj.read(cr, uid, company['company_id'][0], ['agent_id', 'area_manager_id'], context=context)
            if (company['job_id'] == datas['agent_id']) or (company['job_id'] == datas['area_manager_id']):
                result = True
            res[ids[0]] = result
        return res

    def _this_agent(self, cr, uid, ids, name, arg, context=None):
        users_obj = self.pool.get('res.users')
        groups_obj = self.pool.get('res.groups')
        res = {}
        result = False
        for user_data in self.read(cr, uid, ids, ['user_id', 'is_agent', 'area_manager_id'], context=context):
            if user_data['is_agent']:
                area_manager_user_id = False
                if user_data['area_manager_id']:
                    area_manager_user_id = self.read(cr, uid, user_data['area_manager_id'][0], ['user_id'], context=context)
                if user_data['user_id'] and user_data['user_id'][0] == uid:
                    result = True
                elif user_data['area_manager_id'] and area_manager_user_id['user_id'][0] == uid:
                    #if user_data['area_manager_id'][0] == uid:
                    result = True
                else:
                    groups_ids = groups_obj.search(cr, uid, [('name', '=', 'Agent / Manager')])
                    data_users = users_obj.read(cr, uid, uid, ['groups_id'], context=context)
                    for my_group in data_users['groups_id']:
                        if my_group in groups_ids:
                            result = True
                            break
        res[ids[0]] = result
        return res

    def _job_area_manager(self, cr, uid, ids, name, arg, context=None):
        company_obj = self.pool.get('res.company')
        users_obj = self.pool.get('res.users')
        groups_obj = self.pool.get('res.groups')
        res = {}
        result = False
        for company in self.read(cr, uid, ids, ['user_id', 'company_id', 'job_id'], context=context):
            datas = company_obj.read(cr, uid, company['company_id'][0], ['area_manager_id'], context=context)
            if company['job_id'] == datas['area_manager_id']:
                if company['user_id'][0] == uid:
                    result = True
                else:
                    groups_ids = groups_obj.search(cr, uid, [('name', '=', 'Agent / Manager')])
                    data_users = users_obj.read(cr, uid, uid, ['groups_id'], context=context)
                    for my_group in data_users['groups_id']:
                        if my_group in groups_ids:
                            result = True
                            break
            res[ids[0]] = result
        return res

    _columns = {
        'area_manager_desc': fields.function(_manager_description, method=True, string='Area Manager Description', type='char'),
        'is_agent': fields.function(_job_agent, method=True, string='is Agent?', type='boolean', store=True),
        'is_area_manager': fields.function(_job_area_manager, method=True, string='is Area Manager?', type='boolean'),
        'this_agent': fields.function(_this_agent, method=True, string='am i?', type='boolean'),
        'area_manager_id': fields.many2one('hr.employee', 'Area Manager', ondelete='cascade', select=True),
        'res_partner_zone_id': fields.many2one('res.partner.zone', 'Zone', ondelete='cascade'),
    }


class inherit_res_partner_zone(osv.osv):
    _inherit = 'res.partner.zone'
    _columns = {
        'agent_employee_ids': fields.one2many('hr.employee', "res_partner_zone_id", "agent area's"),
    }


class hr_agent_commission(osv.osv):
    _name = 'hr.agent.commission'
    _description = "commission agent's"
    _columns = {
        #fare errore se non mette almeno uno dei due campi
        'product_id': fields.many2one("product.product", "Product", ondelete='cascade'),
        'category_id': fields.many2one("product.category", "Category Product's", ondelete='cascade'),
        'customer_id': fields.many2one("res.partner", "Customer", ondelete='cascade'),
        'commission_percent': fields.float('Commission (%)', digits=(5, 2)),
        'fixed_commission': fields.float('fixed commission', digits=(10, 2)),
        'hr_employee_id': fields.many2one('hr.employee', "Agent", ondelete='cascade'),
    }


class hr_area_manager_commission(osv.osv):
    _name = 'hr.area.manager.commission'
    _description = "area manager's fixed commission"
    _columns = {
        'agent_id': fields.many2one('hr.employee', 'Agent', ondelete='cascade'),
        'commission_percent': fields.float('Commission (%)', digits=(5, 2)),
        'from_revenues': fields.float('From Revenues', digits=(10, 2)),
        'to_revenues': fields.float('To Revenues', digits=(10, 2)),
        'hr_manager_id': fields.many2one('hr.employee', "area manager's", ondelete='cascade'),
    }


class inherit_hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'hr_agent_commission_ids': fields.one2many('hr.agent.commission', "hr_employee_id", "commission agent's"),
        'hr_area_manager_commission_ids': fields.one2many('hr.area.manager.commission', "hr_manager_id", "area manager's fixed commission"),
    }
