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
        'sale_project': fields.related('sale_id', 'project_project', type='many2one', relation='project.project', string=_('Project'), store=False),
    }
    
    def do_partial(self, cr, uid, ids, partial_data, context):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        for picking in self.browse(cr, uid, ids):
            if picking.project_id or picking.sale_project:
                for move in picking.move_lines:
                    values = {
                        'name': move.name,
                        'product': move.product_id,
                        'product_qty': move.product_qty,
                        'product_uom_id': move.product_uom,
                        'account_id': picking.project_id and picking.project_id.analytic_account_id.id or picking.sale_project.analytic_account_id.id,
                        'date': move.date,
                        'ref': picking.name,
                        'origin_document': move
                    }
                    self.pool.get('account.analytic.line').update_or_create_line(cr, uid, values)
        return super(stock_picking, self).do_partial(cr, uid, ids, partial_data, context=context)

    def action_reopen(self, cr, uid, ids, context=None):
        analytic_line_obj = self.pool['account.analytic.line']

        for picking in self.browse(cr, uid, ids):
            for move in picking.move_lines:
                analytic_line_ids = analytic_line_obj.search(cr, uid, [('origin_document', '=', '{model}, {document_id}'.format(model=move._name, document_id=move.id))])
                if analytic_line_ids:
                    analytic_line_obj.unlink(cr, uid, analytic_line_ids)
            
        return super(stock_picking, self).action_reopen(cr, uid, ids, context)


class account_analytic_line(orm.Model):
    _inherit = 'account.analytic.line'
    
    def _get_selection_list(self, cr, uid, context=None):
        #@return a list of tuples. tuples containing model name and name of the record
        model_obj = self.pool.get('ir.model')
        ids = model_obj.search(cr, uid, [('name', 'not ilike', '.')])
        res = model_obj.read(cr, uid, ids, ['model', 'name'])
        return [(r['model'], r['name']) for r in res] + [('', '')]
    
    _columns = {
        'origin_document': fields.reference("Origin Document", selection=_get_selection_list, size=None)
    }
