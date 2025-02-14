# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from osv import fields, orm
from tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class MrpProduction(orm.Model):

    _inherit = 'mrp.production'

    _index_name = 'mrp_production_state_index'
    _index_name2 = 'mrp_production_id_state_index'

    def _auto_init(self, cr, context={}):
        res = super(MrpProduction, self)._auto_init(cr, context)

        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s', (self._index_name,))
        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON mrp_production (state)'.format(name=self._index_name))

        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s', (self._index_name2,))
        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON mrp_production (id, state)'.format(name=self._index_name2))

        return res

    def _compute_project_id(self, cr, uid, ids, field_name, args, context):
        result = {}
        for record in self.browse(cr, uid, ids, context):
            project_id = False
            if record.sale_id:
                project_id = record.sale_id.project_project.id if record.sale_id.project_project else False
            result[record.id] = project_id
        return result

    def _get_project_data(self, cr, uid, arg, context):
        project_model = self.pool['project.project']
        if arg[1] == '=':
            return project_model.read(cr, uid, [arg[2]], ['sale_order_ids'], context)
        else:
            result = project_model.name_search(
                cr, uid, name=arg[2], operator=arg[1], context=context, limit=None)
            if result:
                project_ids = [x[0] for x in result]
                return project_model.read(
                    cr, uid, project_ids, ['sale_order_ids'], context)
        return None

    def _accumulate_sale_order_ids(self, data):
        return [_id for item in data for _id in item['sale_order_ids']]

    def _search_project_id(self, cr, uid, obj, name, args, context=None):
        sale_order_ids = []
        if args:
            for arg in args:
                data = self._get_project_data(cr, uid, arg, context)
                if data:
                    sale_order_ids += self._accumulate_sale_order_ids(data)
            return [('sale_id', 'in', sale_order_ids)]
        return []

    _columns = {
        'is_from_order_requirement': fields.boolean('is from order requirement'),
        'temp_bom_id': fields.many2one(obj='temp.mrp.bom', string='Bill of Material Line', readonly=True, select=1,  ondelete='cascade'),
        'order_requirement_line_id': fields.related('temp_bom_id', 'order_requirement_line_id', string='Order Requirement Line',
                                                    relation='order.requirement.line', type='many2one', readonly=True),
        'level': fields.integer('Level', required=True),
        'sale_id': fields.many2one('sale.order', 'Sale order'),
        'analytic_account_id': fields.many2one('account.analytic.account',
                                               'Analytic Account', ),
        'project_id': fields.function(
            _compute_project_id,
            obj='project.project',
            string='Project',
            fnct_search=_search_project_id,
            method=True, type='many2one'),

    }

    _defaults = {
        'is_from_order_requirement': False,
        'level': 0
    }

    def _make_production_produce_line(self, cr, uid, production, context=None):
        stock_move = self.pool['stock.move']
        move_id = super(MrpProduction, self)._make_production_produce_line(
            cr, uid, production, context=context)
        if production.analytic_account_id:
            stock_move.write(cr, uid, [move_id], {
                'analytic_account_id': production.analytic_account_id.id
            }, context=context)
        return move_id

    def _make_production_consume_line(self, cr, uid, production_line, parent_move_id, source_location_id=False,
                                      context=None):
        stock_move = self.pool['stock.move']
        move_id = super(MrpProduction, self)._make_production_consume_line(
            cr, uid, production_line, parent_move_id,
            source_location_id=source_location_id, context=context)
        production = production_line.production_id
        if production.analytic_account_id:
            stock_move.write(cr, uid, [move_id], {
                'analytic_account_id': production.analytic_account_id.id
            }, context=context)
        return move_id

    def _costs_generate(self, cr, uid, production, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        super(MrpProduction, self)._costs_generate(cr, uid, production, context)
        amount = 0.0
        analytic_line_model = self.pool['account.analytic.line']
        default_account = self.pool['ir.property'].get(cr, uid, 'property_account_expense_categ',
                                                           'product.category', context=context)
        for wc_line in production.workcenter_lines:
            wc = wc_line.workcenter_id
            if wc.costs_journal_id:
                # Cost per hour
                value = wc_line.delay * wc.costs_hour
                account = False
                if production.analytic_account_id:
                    account = production.analytic_account_id
                elif production.sale_id and production.sale_id.project_id:
                    account = production.sale_id.project_id
                if value and account:
                    amount += value
                    analytic_line_vals = {
                        'name': wc_line.name + _(' (H)'),
                        'amount': -value,
                        'account_id': account.id,
                        'general_account_id': wc.costs_general_account_id and wc.costs_general_account_id.id or wc.product_id.property_account_income and wc.product_id.property_account_income.id or default_account.id,
                        'journal_id': wc.costs_journal_id.id,
                        'ref': wc.code,
                        'product_id': wc.product_id and wc.product_id.id or False,
                        'unit_amount': wc_line.hour,
                        'product_uom_id': wc.product_id and wc.product_id.uom_id.id or False
                    }
                    analytic_line_model.create(cr, uid, analytic_line_vals, context)
                # Cost per cycle
                value = wc_line.cycle * wc.costs_cycle

                if value and account:
                    amount += value
                    analytic_line_model.create(cr, uid, {
                        'name': wc_line.name + ' (C)',
                        'amount': -value,
                        'account_id': account.id,
                        'general_account_id': wc.costs_general_account_id.id or wc.product_id.property_account_income and wc.product_id.property_account_income.id or default_account.id,
                        'journal_id': wc.costs_journal_id.id,
                        'ref': wc.code,
                        'product_id': wc.product_id.id,
                        'unit_amount': wc_line.cycle,
                        'product_uom_id': wc.product_id and wc.product_id.uom_id.id or False
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
            return super(MrpProduction, self).action_compute(cr, uid, ids, properties, context)

        results = []

        # If production order was created by order requirement, behaviour is different
        temp_mrp_bom_model = self.pool['temp.mrp.bom']
        uom_model = self.pool['product.uom']
        prod_line_model = self.pool['mrp.production.product.line']
        workcenter_line_model = self.pool['mrp.production.workcenter.line']
        for production in self.browse(cr, uid, ids, context):
            cr.execute('delete from mrp_production_product_line where production_id=%s', (production.id,))
            cr.execute('delete from mrp_production_workcenter_line where production_id=%s', (production.id,))

            bom_point = production.temp_bom_id
            bom_id = production.temp_bom_id.id

            if not (bom_point or bom_id):
                _logger.error('action_compute: Production order %s does not have a bill of material.' % production.name)
                raise orm.except_orm(_('Error'), _("Found a production order to enqueue to, but it does not have a bill of material: ") + production.name)
            factor = uom_model._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            # Forcing routing_id to False, the lines are linked directly to temp_mrp_bom
            res = temp_mrp_bom_model._temp_mrp_bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, context)
            results = res[0]
            results2 = res[1]
            for line in results:
                line['production_id'] = production.id
                prod_line_model.create(cr, uid, line, context)
            if not results2 and production.routing_id:
                bom_point = production.bom_id
                original_bom_res = self.pool['mrp.bom']._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=production.routing_id.id)

                results2 = original_bom_res[1]

            for line in results2:
                line['production_id'] = production.id
                workcenter_line_model.create(cr, uid, line, context)
        return len(results)

