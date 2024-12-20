# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from tools.translate import _
from datetime import date, datetime

from openerp.osv import orm, fields
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

STATE_SELECTION = [
    ('draft', 'Draft'),
    ('done', 'Confirmed'),
    ('cancel', 'Cancelled')
]


class order_requirement(orm.Model):

    _name = 'order.requirement'

    def _get_day(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for requirement in self.read(cr, uid, ids, ['date'], context=context):
            res[requirement['id']] = {
                'week_nbr': False,
            }
            if not requirement['date']:
                continue

            start_date = datetime.strptime(requirement['date'], DEFAULT_SERVER_DATE_FORMAT)
            start_date = date(start_date.year, start_date.month, start_date.day)

            # mese in italiano start_date.strftime('%B').capitalize()
            res[requirement['id']] = {
                'week_nbr': start_date.isocalendar()[1],
                'month': int(start_date.strftime("%m")),
            }

        return res

    _rec_name = 'sale_order_id'

    _order = 'state, date'

    def name_get(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = []
        for line in self.read(cr, uid, ids, [self._rec_name], context):
            res.append((line['id'], line[self._rec_name][1]))
        return res

    def _order_state(self, cr, uid, ids, name, args, context=None):
        # order_requirement_model = self.pool['order.requirement']
        # order_requirement_line_model = self.pool['order.requirement.line']
        purchase_order_model = self.pool['purchase.order']
        # purchase_order_line_model = self.pool['purchase.order.line']
        temp_mrp_bom_model = self.pool['temp.mrp.bom']
        mrp_production_model = self.pool['mrp.production']
        stock_move_model = self.pool['stock.move']

        res = dict.fromkeys(ids, {})

        cr.execute(
            "select order_requirement_id, id from order_requirement_line where order_requirement_id in (%s) group by order_requirement_id, id" % ",".join(
                [str(x) for x in ids if x]))
        order_requirement_line2_ids = cr.fetchall()

        for order_id in ids:
            res[order_id] = {
                'production_orders_state': '',
                'purchase_orders_approved': '',
                'purchase_orders_state': '',
            }
            tot = 0
            done_order_approved = 0
            tot_order_state = 0

            order_requirement_line_ids = [x[1] for x in order_requirement_line2_ids if x[0] == order_id]
            temp_bom_ids = list(set(
                temp_mrp_bom_model.search(cr, uid, [('order_requirement_line_id', 'in', order_requirement_line_ids)],
                                        context=context)))
            if temp_bom_ids:
                cr.execute(
                    "select mrp_production_id from temp_mrp_bom where id in (%s) group by mrp_production_id" % ",".join(
                        [str(x) for x in temp_bom_ids if x]))
                query_result = cr.fetchall()
                production_ids = list(set([x[0] for x in query_result if x[0]]))
                tot = len(production_ids)
                done = len(mrp_production_model.search(cr, uid, [('id', 'in', production_ids), ('state', '=', 'done')],
                                                     context=context))
            purchase_order_ids = []
            if order_requirement_line_ids:
                cr.execute(
                    "select purchase_order_id from order_requirement_line_purchase_order_rel where order_requirement_line_id in (%s)" % ",".join(
                        [str(x) for x in order_requirement_line_ids if x]))
                query_result = cr.fetchall()
                purchase_order_ids = list(set([x[0] for x in query_result if x[0]]))

            tot_order_approved = len(purchase_order_ids)
            if purchase_order_ids:
                done_order_approved = len(purchase_order_model.search(cr, uid, [('id', 'in', purchase_order_ids),
                                                                              ('state', 'in', ('approved', 'done'))],
                                                                    context=context))

                cr.execute(
                    "SELECT  stock_move.id FROM stock_move, purchase_order_line, purchase_order WHERE stock_move.purchase_line_id = purchase_order_line.id AND purchase_order_line.order_id = purchase_order.id AND purchase_order.id in (%s)" % ",".join(
                        [str(x) for x in purchase_order_ids if x]))
                query_result = cr.fetchall()
                stock_move_ids = list(set([x[0] for x in query_result if x[0]]))
                tot_order_state = len(stock_move_ids)
                done_order_state = len(
                    stock_move_model.search(cr, uid, [('id', 'in', stock_move_ids), ('state', '=', 'done')],
                                          context=context))

            if tot > 0:
                res[order_id]['production_orders_state'] = '%d/%d' % (done, tot)
            if tot_order_approved > 0:
                res[order_id]['purchase_orders_approved'] = '%d/%d' % (done_order_approved, tot_order_approved)
            if tot_order_state > 0:
                res[order_id]['purchase_orders_state'] = '%d/%d' % (done_order_state, tot_order_state)

        return res

    _columns = {
        'date': fields.date('Data'),
        'sale_order_id': fields.many2one(
            string='Order',
            obj='sale.order',
            readonly=True,
            states={'draft': [('readonly', False)]},
            required=True,
            ondelete='cascade',
            select=True,
            auto_join=True
        ),
        'client_order_ref': fields.related('sale_order_id', 'client_order_ref', type='char', string="Customer Reference"),
        'customer_id': fields.related('sale_order_id', 'partner_id', type='many2one', relation='res.partner', string='Customer', store=False),
        'user_id': fields.many2one(obj='res.users', string='User', readonly=True,
                                   states={'draft': [('readonly', False)]}, ),
        'week_nbr': fields.function(_get_day, method=True, multi='day_of_week', type="integer", string="Week Number", store={
            'order.requirement': (lambda self, cr, uid, ids, c={}: ids, ['date'], 30),
        }),
        'month': fields.function(_get_day, type='integer', string='Month', method=True, multi='day_of_week', store={
            'order.requirement': (lambda self, cr, uid, ids, c={}: ids, ['date'], 30),
        }),
        'state': fields.selection(STATE_SELECTION, 'Order State', readonly=True),
        'order_requirement_line_ids': fields.one2many('order.requirement.line', 'order_requirement_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'full_order_requirement_line_ids': fields.one2many('full.order.requirement.line', 'order_requirement_id', 'Full Order Lines', readonly=True),
        'note': fields.text('Order Note'),
        'internal_note': fields.related('sale_order_id', 'picking_ids', 'internal_note', type='text', string='Internal Note'),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'production_product_id': fields.related('order_requirement_line_ids', 'temp_mrp_bom_ids', 'product_id', type='many2one', relation='product.product',
                                     string='Product Production'),
        'product_id': fields.related('order_requirement_line_ids', 'product_id', type='many2one', relation='product.product',
                                     string='Product'),
        'new_product_id': fields.related('order_requirement_line_ids', 'new_product_id', type='many2one', relation='product.product',
                                     string='Choosen Product'),
        'production_orders_state': fields.function(_order_state, method=True, type='char', size=16, multi='order_state',
                                                   string='Prod. orders', readonly=True),
        'purchase_orders_approved': fields.function(_order_state, method=True, type='char', size=16,multi='order_state',
                                                    string='Purch. orders approved', readonly=True),
        'purchase_orders_state': fields.function(_order_state, method=True, type='char', size=16, multi='order_state',
                                                 string='Deliveries', readonly=True),
        'group_purchase_by_sale_order': fields.boolean(
            string="Group Purchase by Sale Order",
            readonly=True,
            states={'draft': [('readonly', False)]},
            default=False
        )
    }

    _defaults = {
        'date': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }

    _order = 'date desc'

    def set_state_draft(self, cr, uid, ids, context):
        temp_mrp_bom_model = self.pool['temp.mrp.bom']
        temp_mrp_routing_model = self.pool['temp.mrp.routing']
        order_requirement_line_model = self.pool['order.requirement.line']
        purchase_order_model = self.pool['purchase.order']
        line_ids = order_requirement_line_model.search(cr, uid, [('order_requirement_id', 'in', ids), ('state', '!=', 'draft')], context=context)
        purchase_order = []
        production_order = []
        description = []
        purchase_order_to_clear = {}
        if line_ids:
            # search PO #
            purchase_order_ids = []
            # for order in order_requirement_line_model.read(cr, uid, line_ids, ['purchase_order_ids'], context=context):
            #     purchase_order_ids += order['purchase_order_ids']
            # purchase_order_ids = list(set(purchase_order_ids))
            # if purchase_order_ids:
            #     for order in purchase_order_model.read(cr, uid, purchase_order_ids, ['name', 'state'], context=context):
            #         purchase_order.append(order['name'])

            order_ids = temp_mrp_bom_model.search(cr, uid, [('order_requirement_line_id', 'in', line_ids), ('purchase_order_id', '!=', False)], context=context)
            production_ids = temp_mrp_bom_model.search(cr, uid, [('order_requirement_line_id', 'in', line_ids), ('mrp_production_id', '!=', False)], context=context)
            for temp_mrp_bom in temp_mrp_bom_model.browse(cr, uid, list(set(production_ids + order_ids)), context):
                if temp_mrp_bom.purchase_order_id:
                    purchase_order_id = temp_mrp_bom.purchase_order_id
                    if purchase_order_id.state == 'draft':
                        if purchase_order_id not in purchase_order_to_clear:
                            purchase_order_to_clear[purchase_order_id] = []
                        purchase_order_to_clear[purchase_order_id].append(temp_mrp_bom.sale_order_id.id)
                        purchase_order_line_id = temp_mrp_bom.purchase_order_line_id
                        if purchase_order_line_id:
                            purchase_qty = purchase_order_line_id.product_qty
                            line_qty = temp_mrp_bom.product_qty
                            if line_qty == purchase_qty:
                                purchase_order_line_id.unlink()
                            else:
                                purchase_order_line_id.write({
                                    'product_qty': purchase_qty - line_qty,
                                    'order_requirement_ids': [(3, temp_mrp_bom.order_requirement_line_id.order_requirement_id.id)],
                                    'order_requirement_line_ids': [(3, temp_mrp_bom.order_requirement_line_id.id)],
                                    'temp_mrp_bom_ids': [(3, temp_mrp_bom.id)],
                                })
                        temp_mrp_bom.write({
                            'purchase_order_id': False,
                            'purchase_order_line_id': False,
                            'state': 'draft'
                        })
                    else:
                        purchase_order.append(purchase_order_id.name)

                    # if temp_mrp_bom.purchase_order_id.name not in purchase_order:
                    #     purchase_order.append(temp_mrp_bom.purchase_order_id.name)
                if temp_mrp_bom.mrp_production_id:
                    if temp_mrp_bom.mrp_production_id.state == 'draft':
                        temp_mrp_bom.mrp_production_id.unlink()
                        temp_mrp_bom.write({
                            'mrp_production_id': False,
                            'state': 'draft'
                        })
                    elif temp_mrp_bom.mrp_production_id.name not in production_order:
                        production_order.append(temp_mrp_bom.mrp_production_id.name)

        for po in purchase_order_to_clear:
            po.write({
                'sale_order_ids': [(3, so_id) for so_id in list(set(purchase_order_to_clear[po]))]
            })

        if purchase_order or production_order:
            description.append(_(u'Please delete below'))
        if purchase_order:
            description.append(_(u'Order'))
            description += purchase_order
        if production_order:
            description.append(_(u'Production'))
            description += production_order

        if description:
            raise orm.except_orm(_(u'Error !'), '\n'.join(description))

        order_requirement_line_model.write(cr, uid, line_ids, {'state': 'draft', 'new_product_id': False}, context)
        all_line_to_clear_ids = temp_mrp_bom_model.search(cr, uid, [('order_requirement_line_id', 'in', line_ids)],
                                                          context=context)
        temp_mrp_bom_model.write(cr, uid, all_line_to_clear_ids, {'active': False}, context)

        temp_mrp_routing_ids = temp_mrp_routing_model.search(cr, uid, [('order_requirement_line_id', 'in', line_ids)],
                                                          context=context)
        temp_mrp_routing_model.unlink(cr, uid, temp_mrp_routing_ids, context=context)

        order_requirement_line_model.action_reload_bom(cr, uid, line_ids, context)
        self.write(cr, uid, ids, {'state': 'draft'}, context)
        return True

    # def set_state_done(self, cr, uid, ids, context):
        # TODO set_state_done, now commented in view
        # pass
        # self.write(cr, uid, ids, {'state': 'done'})

    def action_view_order_requirement(self, cr, uid, ids, context=None):

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'sale_order_requirement', 'action_view_order_requirement')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        # compute the number of invoices to display

        # choose the view_mode accordingly
        if len(ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, ids)) + "])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'sale_order_requirement', 'view_order_requirement_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['view_mode'] = 'page'
            result['res_id'] = ids and ids[0] or False

        return result

    def action_view_purchase_order(self, cr, uid, ids, context=None):
        order = self.browse(cr, uid, ids, context)[0]
        purchase_ids = []
        for line in order.order_requirement_line_ids:
            purchase_ids += [po.id for po in line.purchase_order_ids]

        purchase_ids = list(set(purchase_ids))
        mod_model = self.pool['ir.model.data']
        form_id = mod_model.get_object_reference(cr, uid, 'purchase', 'purchase_order_form')
        form_res = form_id and form_id[1] or False
        tree_id = mod_model.get_object_reference(cr, uid, 'purchase', 'purchase_order_tree')
        tree_res = tree_id and tree_id[1] or False
        return {
            'domain': "[('id', 'in', %s)]" % purchase_ids,
            'name': _('Purchase Order'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'view_id': False,
            'views': [(tree_res, 'tree'), (form_res, 'form')],
            'context': "{'type':'out_refund'}",
            'type': 'ir.actions.act_window',
        }

    def action_view_manufacturing_order(self, cr, uid, ids, context=None):
        if isinstance(ids, (long, int)):
            ids = [ids]

        order_requirement_line_ids = self.pool['order.requirement.line'].search(cr, uid,
                                                                                [('order_requirement_id', 'in', ids)],
                                                                                context=context)
        # order = self.browse(cr, uid, ids, context)[0]
        # production_ids = []
        # for line in order.order_requirement_line_ids:
        #     for bom_line in line.temp_mrp_bom_ids:
        #         if bom_line.mrp_production_id.id:
        #             production_ids.append(bom_line.mrp_production_id.id)
        # production_ids = list(set(production_ids))

        production_ids = self.pool['mrp.production'].search(cr, uid, [('order_requirement_line_id', 'in', order_requirement_line_ids)], context=context)

        mod_model = self.pool['ir.model.data']
        act_model = self.pool['ir.actions.act_window']
        action_id = mod_model.get_object_reference(cr, uid, 'mrp', 'mrp_production_action')
        action_res = action_id and action_id[1]
        action = act_model.read(cr, uid, action_res, [], context)
        action.update({
            'domain': "[('id', 'in', %s)]" % production_ids,
            'context': "{}"
        })
        return action

    def action_force_all(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not ids:
            return False
        # order_requirement = self.browse(cr, uid, ids, context)[0]
        # order_requirement_line_ids = []
        # for line in order_requirement.order_requirement_line_ids:
        #     if line.state == 'draft':
        #         order_requirement_line_ids.append(line.id)

        res_id = self.pool['wizard.requirement'].create(cr, uid, {
            'order_id': ids[0]
            #'order_line_ids': [(6, 0, order_requirement_line_ids)]
        }, context)

        action_vals = {
            'type': 'ir.actions.act_window',
            'name': _('Wizard Requirement'),
            'res_model': 'wizard.requirement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [],
            'target': 'new',
            'context': {},
            'res_id': res_id
        }
        return action_vals
