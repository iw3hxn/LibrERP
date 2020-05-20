# -*- encoding: utf-8 -*-
################################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
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
################################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'project_id': fields.many2one('project.project', _('Project'), required=False),
        'account_id': fields.related('sale_id', 'project_id', type='many2one', relation='account.analytic.account', string=_('Analytic Account'), store=False),
        'sale_project': fields.related('sale_id', 'project_project', type='many2one', relation='project.project', string=_('Project'), store=False),
    }

    def onchange_account_id(self, cr, uid, ids, project_id, context=None):
        res = {}
        if project_id:
            context = context or self.pool['res.users'].context_get(cr, uid)
            project = self.pool['project.project'].browse(cr, uid, project_id, context)
            res.update({
                'account_id': project.analytic_account_id.id,
                'sale_project': project.id
            })
        return {'value': res}

    def onchange_sale_id(self, cr, uid, ids, sale_id):
        res = {}
        if sale_id:
            context = self.pool['res.users'].context_get(cr, uid)
            order = self.pool['sale.order'].browse(cr, uid, sale_id, context)
            if order.project_project:
                res.update({
                    'project_id': order.project_project.id
                })
        return {'value': res}

    def _commit_cost(self, cr, uid, ids, context=None):
        for picking in self.browse(cr, uid, ids, context):
            if picking.project_id or picking.sale_project or picking.account_id:
                for move in picking.move_lines:
                    values = {
                        'name': move.name,
                        'product': move.product_id,
                        'product_qty': move.product_qty,
                        'product_uom_id': move.product_uom and move.product_uom.id,
                        'account_id': picking.account_id and picking.account_id.id or picking.project_id and picking.project_id.analytic_account_id.id or picking.sale_project.analytic_account_id.id,
                        'date': move.date,
                        'ref': picking.name,
                        'origin_document': move
                    }
                    self.pool['account.analytic.line'].update_or_create_line(cr, uid, move, values, context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        result = super(stock_picking, self).action_done(cr, uid, ids, context=context)
        picking_ids = self.search(cr, uid, [('id', 'in', ids), ('type', '=', 'internal')], context=context)
        if picking_ids:
            self._commit_cost(cr, uid, picking_ids, context)
        return result
    
    def do_partial(self, cr, uid, ids, partial_data, context):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        self._commit_cost(cr, uid, ids, context)
        return super(stock_picking, self).do_partial(cr, uid, ids, partial_data, context=context)

    def action_reopen(self, cr, uid, ids, context=None):
        analytic_line_obj = self.pool['account.analytic.line']

        for picking in self.browse(cr, uid, ids, context=context):
            for move in picking.move_lines:
                analytic_line_ids = analytic_line_obj.search(cr, uid, [('origin_document', '=', '{model}, {document_id}'.format(model=move._name, document_id=move.id))], context=context)
                if analytic_line_ids:
                    analytic_line_obj.unlink(cr, uid, analytic_line_ids, context=context)

        return super(stock_picking, self).action_reopen(cr, uid, ids, context=context)

