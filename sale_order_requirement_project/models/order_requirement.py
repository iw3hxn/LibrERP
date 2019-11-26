# -*- coding: utf-8 -*-
# © 2019 Didotech srl (www.didotech.com)

from tools.translate import _

from openerp.osv import orm, fields


class OrederRequirement(orm.Model):

    _inherit = 'order.requirement'

    _columns = {
        'project_id': fields.related('sale_order_id', 'project_project', type='many2one', relation='project.project', string="Project", store=False, readonly=True),
    }

    def create_project(self, cr, uid, ids, context=None):

        for order_requirement in self.browse(cr, uid, ids, context):
            order = order_requirement.sale_order_id
            shop = order_requirement.sale_order_id.shop_id

            if order.order_policy == 'picking':
                invoice_ratio = 1
            else:
                invoice_ratio = 3

            project_values = {
                'name': order.name.split(' ')[0],
                'partner_id': order.partner_id and order.partner_id.id or False,
                'contact_id': order.partner_order_id and order.partner_order_id.id or False,
                'pricelist_id': order.pricelist_id and order.pricelist_id.id,
                'to_invoice': invoice_ratio,
                'state': 'pending',
                'warn_manager': True,
                'user_id': shop.project_manager_id and shop.project_manager_id.id or order.user_id and order.user_id.id or False,
            }

            if shop.member_ids:
                project_values['members'] = [(6, 0, [user.id for user in shop.member_ids])]

            if shop.project_id:
                project_values['parent_id'] = shop.project_id.id
            ctx = context.copy()
            ctx.update({
                'model': 'sale.order',
            })
            project_id = self.pool['project.project'].create(cr, uid, project_values, context=ctx)

            self.pool['sale.order'].write(cr, uid, order.id, {'project_project': project_id}, context=context)

        return True

