# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from osv import fields, orm
from tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class mrp_production(orm.Model):

    _inherit = 'mrp.production'

    _columns = {
        'is_from_order_requirement': fields.boolean('is from order requirement'),
        'temp_bom_id': fields.many2one('temp.mrp.bom', 'Bill of Material Line', readonly=True),
        'order_requirement_line_id': fields.related('temp_bom_id', 'order_requirement_line_id', string='Order Requirement Line',
                                                    relation='order.requirement.line', type='many2one', readonly=True),
        'level': fields.integer('Level', required=True),
        'sale_id': fields.many2one('sale.order', 'Sale order'),
        'analytic_account_id': fields.many2one('account.analytic.account',
                                               'Analytic Account', ),
    }

    _defaults = {
        'is_from_order_requirement': False,
        'level': 0
    }

    def _make_production_produce_line(self, cr, uid, production, context=None):
        stock_move = self.pool['stock.move']
        move_id = super(mrp_production, self)._make_production_produce_line(
            cr, uid, production, context=context)
        if production.analytic_account_id:
            stock_move.write(cr, uid, [move_id], {
                'analytic_account_id': production.analytic_account_id.id
            }, context=context)
        return move_id

    def _make_production_consume_line(self, cr, uid, production_line, parent_move_id, source_location_id=False,
                                      context=None):
        stock_move = self.pool['stock.move']
        move_id = super(mrp_production, self)._make_production_consume_line(
            cr, uid, production_line, parent_move_id,
            source_location_id=source_location_id, context=context)
        production = production_line.production_id
        if production.analytic_account_id:
            stock_move.write(cr, uid, [move_id], {
                'analytic_account_id': production.analytic_account_id.id
            }, context=context)
        return move_id

    def _costs_generate(self, cr, uid, production):
        context = self.pool['res.users'].context_get(cr, uid)
        super(mrp_production, self)._costs_generate(cr, uid, production)
        amount = 0.0
        analytic_line_obj = self.pool['account.analytic.line']
        for wc_line in production.workcenter_lines:
            wc = wc_line.workcenter_id
            if wc.costs_journal_id:
                # Cost per hour
                value = wc_line.delay * wc.costs_hour
                account = False
                if production.analytic_account_id:
                    account = production.analytic_account_id
                if production.sale_id and production.sale_id.project_id:
                    account = production.sale_id.project_id.id
                if value and account:
                    amount += value
                    analytic_line_obj.create(cr, uid, {
                        'name': wc_line.name + _(' (H)'),
                        'amount': value,
                        'account_id': account,
                        'general_account_id': wc.costs_general_account_id and wc.costs_general_account_id.id or wc.product_id.property_account_income and wc.product_id.property_account_income.id,
                        'journal_id': wc.costs_journal_id.id,
                        'ref': wc.code,
                        'product_id': wc.product_id and wc.product_id.id or False,
                        'unit_amount': wc_line.hour,
                        'product_uom_id': wc.product_id and wc.product_id.uom_id.id or False
                    }, context)
                # Cost per cycle
                value = wc_line.cycle * wc.costs_cycle

                if value and account:
                    amount += value
                    analytic_line_obj.create(cr, uid, {
                        'name': wc_line.name + ' (C)',
                        'amount': value,
                        'account_id': account,
                        'general_account_id': wc.costs_general_account_id.id or wc.product_id.property_account_income and wc.product_id.property_account_income.id,
                        'journal_id': wc.costs_journal_id.id,
                        'ref': wc.code,
                        'product_id': wc.product_id.id,
                        'unit_amount': wc_line.cycle,
                        'product_uom_id': wc.product_id  and wc.product_id.uom_id.id or False
                    }, context)
        return amount

    def action_compute(self, cr, uid, ids, properties=[], context=None):
        """ Computes bills of material of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        If necessary, redirects to temp.mrp.bom instead of mrp.bom
        """
        # action_compute is the Entry point for intercepting the mrp production
        if not ids:
            return 0

        if isinstance(ids, (int, long)):
            ids = [ids]

        productions = self.browse(cr, uid, ids, context)

        # NOTE: SINGLE PRODUCTION (not supported for multiple lines, problems with return len(results) )

        if not productions[0].is_from_order_requirement:
            return super(mrp_production, self).action_compute(cr, uid, ids, properties, context)

        results = []

        # If production order was created by order requirement, behaviour is different
        temp_mrp_bom_obj = self.pool['temp.mrp.bom']
        uom_obj = self.pool['product.uom']
        prod_line_obj = self.pool['mrp.production.product.line']
        workcenter_line_obj = self.pool['mrp.production.workcenter.line']
        for production in self.browse(cr, uid, ids, context):
            cr.execute('delete from mrp_production_product_line where production_id=%s', (production.id,))
            cr.execute('delete from mrp_production_workcenter_line where production_id=%s', (production.id,))

            bom_point = production.temp_bom_id
            bom_id = production.temp_bom_id.id

            if not (bom_point or bom_id):
                _logger.error('action_compute: Production order %s does not have a bill of material.' % production.name)
                raise orm.except_orm(_('Error'), _("Found a production order to enqueue to, but it does not have a bill of material: ") + production.name)
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            # Forcing routing_id to False, the lines are linked directly to temp_mrp_bom
            res = temp_mrp_bom_obj._temp_mrp_bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, context)
            results = res[0]
            results2 = res[1]
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line, context)
            if not results2 and production.routing_id:
                bom_point = production.bom_id
                original_bom_res = self.pool['mrp.bom']._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=production.routing_id.id)

                results2 = original_bom_res[1]

            for line in results2:
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line, context)
        return len(results)

    def edit_production(self, cr, uid, ids, context=None):
        if not ids:
            return
        context = self.pool['res.users'].context_get(cr, uid)
        stock_move_obj = self.pool['stock.move']
        stock_move_temp_obj = self.pool['stock.move.temp']
        mrp_production_wizard_obj = self.pool['mrp.production.wizard']

        production = self.browse(cr, uid, ids[0], context)

        # COPY STOCK.MOVE DATA

        wizard_id = mrp_production_wizard_obj.create(cr, uid, {'production_id': production.id}, context)
        # wizard = mrp_production_wizard_obj.browse(cr, uid, wizard_id, context)

        # All moves, to be consumed and consumed
        move_lines = production.move_lines
        move_lines.extend(production.move_lines2)

        for line in move_lines:
            vals = {
                'production_id': production.id,
                'orig_stock_move_id': line.id,
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom': line.product_uom.id,
                'location_id': line.location_id.id,
                'location_dest_id': line.location_dest_id.id,
                'prodlot_id': line.prodlot_id.id,
                'is_consumed': line.state == 'done',
                'state': line.state,
                'wizard_id': wizard_id
            }
            # if vals['is_consumed']:
            #     mrp_production_wizard_obj.write(cr, uid, wizard_id, {'move_lines2': (0, False, vals)}, context=context)
            # else:
            #     mrp_production_wizard_obj.write(cr, uid, wizard_id, {'move_lines': (0, False, vals)}, context=context)
            # if vals['is_consumed']:
            #     mrp_production_wizard_obj.write(cr, uid, wizard_id, {'move_lines2': (0, False, vals)}, context=context)
            # else:
            #     mrp_production_wizard_obj.write(cr, uid, wizard_id, {'move_lines': (0, False, vals)}, context=context)

            stock_move_temp_obj.create(cr, uid, vals, context)

        view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'sale_order_requirement', 'view_edit_mrp_products_wizard')
        view_id = view and view[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Edit Products'),
            'res_model': 'mrp.production.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'target': 'new',
            'res_id': wizard_id
        }

