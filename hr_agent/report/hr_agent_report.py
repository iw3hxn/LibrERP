# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Didotech SRL (info at didotech.com)
#                          All Rights Reserved.
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

import tools
from osv import fields, osv


class hr_agent_customer_commission(osv.osv):
    _name = "hr.agent.customer.commission"
    _description = "commission to customer's"
    _auto = False
    _rec_name = 'date'
    _columns = {
        'date': fields.date('Date', readonly=True),
        'date_confirm': fields.date('Date Confirm', readonly=True),
        'hr_employee_id': fields.many2one('hr.employee', "Agent", ondelete='cascade', readonly=True),
        'year': fields.char('Year', size=4, readonly=True),
        'month': fields.selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                                   ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
                                   ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month', readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'trimester': fields.integer('Trimester', readonly=True),
        'sale_order_id': fields.many2one("sale.order", "Sale Order", readonly=True),
        'customer_id': fields.many2one("res.partner", "Customer", readonly=True),
        'zone_id': fields.many2one("res.partner.zone", "Zone", readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'hr_employee_id': fields.many2one('res.users', 'Agent', readonly=True),
        'state': fields.selection([
            ('draft', 'Quotation'),
            ('waiting_date', 'Waiting Schedule'),
            ('manual', 'Manual In Progress'),
            ('progress', 'In Progress'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], 'Order State', readonly=True),
        'price_total': fields.float('Total Price', readonly=True),
        'sale_amount': fields.float("Commission Order's", digits=(16, 2), readonly=True),
        'amount': fields.float("Commission's Receivable", digits=(16, 2), readonly=True),
        'invoice_amount': fields.float('Commission Received', digits=(16, 2), readonly=True),
        'amount_for_graph': fields.float('Commission Amount', digits=(16, 2), readonly=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', readonly=True),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', readonly=True),
    }
    _order = 'date desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'hr_agent_customer_commission')
        cr.execute("""
            create or replace view hr_agent_customer_commission as (
                select
                     min(s.id) as id,
                     s.amount_total as price_total,
                     s.date_order as date,
                     s.date_confirm as date_confirm,
                     to_char(s.date_order, 'YYYY') as year,
                     to_char(s.date_order, 'MM') as month,
                     to_char(s.date_order, 'YYYY-MM-DD') as day,
                     s.internal_user_id as hr_employee_id,
                     s.id as sale_order_id,
                     s.trimester as trimester,
                     s.sale_commission_amount as sale_amount,
                     (case when s.flag_paid = True then
                         s.sale_commission_amount
                     else
                         0.0
                     end) as amount,
                     (case when s.state in ('cancel') then
                         s.sale_commission_amount
                     else
                         0.0
                     end) as invoice_amount,
                     s.sale_commission_amount as amount_for_graph,
                     p.res_partner_zone_id as zone_id,
                     s.partner_id as customer_id,
                     s.company_id as company_id,
                     s.state,
                     s.pricelist_id as pricelist_id,
                     s.project_id as analytic_account_id
                from
                     sale_order s
                     left join res_partner p on (p.id = s.partner_id)
                where
                     s.state not in ('draft','cancel')
                 group by
                     s.amount_total,
                     s.date_order,
                     s.date_confirm,
                     s.internal_user_id,
                     s.id,
                     s.trimester,
                     s.sale_commission_amount,
                     s.flag_paid,
                     s.partner_id,
                     p.res_partner_zone_id,
                     s.company_id,
                     s.state,
                     s.pricelist_id,
                     s.project_id
            )
        """)

#    def init(self, cr):
#        tools.drop_view_if_exists(cr, 'hr_agent_customer_commission')
#        cr.execute("""
#            create or replace view hr_agent_customer_commission as (
#                select
#                    min(s.id) as id,
#                    l.product_id as product_id,
#                    t.uom_id as product_uom,
#                    sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
#                    sum(l.product_uom_qty * l.price_unit * (100.0-l.discount) / 100.0) as price_total,
#                    s.date_order as date,
#                    s.date_confirm as date_confirm,
#                    to_char(s.date_order, 'YYYY') as year,
#                    to_char(s.date_order, 'MM') as month,
#                    to_char(s.date_order, 'YYYY-MM-DD') as day,
#                    s.internal_user_id as hr_employee_id,
#                    s.id as sale_order_id,

#                    (case when s.state in ('waiting_date','manual','progress') then
#                         s.sale_commission_amount
#                        else
#                         0.0
#                        end) as sale_amount,

#                    s.partner_id as customer_id,
#                    s.company_id as company_id,
#                    s.state,
#                    t.categ_id as categ_id,
#                    s.pricelist_id as pricelist_id,
#                    s.project_id as analytic_account_id
#                from
#                    sale_order s
#                    left join sale_order_line l on (s.id=l.order_id)
#                        left join product_product p on (l.product_id=p.id)
#                            left join product_template t on (p.product_tmpl_id=t.id)
#                    left join product_uom u on (u.id=l.product_uom)
#                    left join product_uom u2 on (u2.id=t.uom_id)
#                group by
#                    l.product_id,
#                    l.product_uom_qty,
#                    l.order_id,
#                    t.uom_id,
#                    t.categ_id,
#                    s.date_order,
#                    s.date_confirm,
#                    s.internal_user_id,
#                    s.id,
#                    s.partner_id,
#                    s.company_id,
#                    s.state,
#                    s.pricelist_id,
#                    s.project_id
#            )
#        """)

hr_agent_customer_commission()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
