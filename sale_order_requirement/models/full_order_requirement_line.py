# -*- coding: utf-8 -*-

import tools
from openerp.addons.sale_order_requirement.models.order_requirement import STATE_SELECTION
import decimal_precision as dp
from openerp.osv import orm, fields


class FullOrderRequirementLine(orm.Model):

    _name = 'full.order.requirement.line'
    _rec_name = 'product_id'
    _auto = False
    _order = 'bom_id, bom_parent_id'

    def get_color(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.read(cr, uid, ids, ['level'], context):
            row_color = self.pool['temp.mrp.bom'].get_color_bylevel(line['level'])
            res[line['id']] = row_color
        return res

    def action_view_order_requirement(self, cr, uid, ids, context):
        order = self.browse(cr, uid, ids, context)[0]

        mod_model = self.pool['ir.model.data']
        act_model = self.pool['ir.actions.act_window']
        action_id = mod_model.get_object_reference(cr, uid, 'sale_order_requirement', 'action_view_order_requirement')
        action_res = action_id and action_id[1]
        action = act_model.read(cr, uid, action_res, [], context)
        action.update({
            'domain': "[('id', 'in', %s)]" % [order.order_requirement_id.id],
            'context': "{}"
        })
        return action

    _columns = {
        'level': fields.integer("Level"),
        'level_name': fields.char('Level Name'),
        'product_id': fields.many2one('product.product', string='Original Product', readonly=True),
        'order_requirement_id': fields.many2one('order.requirement', string='Order Requirement'),
        'supplier_id': fields.many2one('res.partner', string='Supplier', readonly=True,
                                       states={'draft': [('readonly', False)]}),
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoS'), readonly=True,
                            states={'draft': [('readonly', False)]}),
        'product_uom': fields.many2one('product.uom', 'UOM'),
        'user_id': fields.many2one('res.users', 'User'),

        'is_manufactured': fields.boolean('Manufacture'),
        'buy': fields.boolean('Buy'),

        'state': fields.selection(STATE_SELECTION, string='State'),

        'categ_id': fields.many2one('product.category', string='Category'),

        'bom_parent_id': fields.integer("BOM Parent ID"),
        'bom_id': fields.integer("BOM ID"),
        'is_leaf': fields.boolean('Leaf', readonly=True),
        'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True,
                                     store=False),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'full_order_requirement_line')

        cr.execute("""
            CREATE or REPLACE view full_order_requirement_line AS (
                SELECT 
                    *,
                    row_number() OVER ()::INTEGER AS id
                    
                    FROM ( 
                        SELECT 
                            temp_mrp_bom.is_leaf, 
                            temp_mrp_bom.bom_id AS bom_parent_id,
                            temp_mrp_bom.id AS bom_id,
                            temp_mrp_bom.level_name,
                            temp_mrp_bom.level,
                            temp_mrp_bom.product_id,
                            order_requirement.id AS order_requirement_id,
                            temp_mrp_bom.supplier_id,
                            temp_mrp_bom.product_qty AS qty,
                            temp_mrp_bom.product_uom,
                            temp_mrp_bom.user_id,
                            temp_mrp_bom.state,
                            temp_mrp_bom.buy,
                            temp_mrp_bom.is_manufactured,
                            product_template.categ_id,
                            temp_mrp_bom.order_requirement_line_id,
                            temp_mrp_bom.sequence
                        
                        FROM order_requirement,
                            order_requirement_line,
                            temp_mrp_bom,
                            product_product,
                            product_template
                        WHERE temp_mrp_bom.order_requirement_line_id = order_requirement_line.id 
                                AND order_requirement_line.order_requirement_id = order_requirement.id 
                                AND temp_mrp_bom.product_id = product_product.id 
                                AND product_product.product_tmpl_id = product_template.id 
                                AND temp_mrp_bom.active = true
                        
                        UNION
                        
                        SELECT 
                            True AS is_leaf,
                            0 AS bom_parent_id,
                            0 AS bom_id,
                            ''::character varying AS level_name,
                            0 AS level,
                            order_requirement_line.product_id,
                            order_requirement.id AS order_requirement_id,
                            order_requirement_line.supplier_id,
                            order_requirement_line.qty,
                            product_template.uom_id AS product_uom,
                            order_requirement_line.user_id,
                            order_requirement_line.state,
                            order_requirement_line.buy,
                            order_requirement_line.is_manufactured,
                            product_template.categ_id,
                            order_requirement_line.id AS order_requirement_line_id,
                            order_requirement_line.id AS sequence
                        FROM order_requirement,
                            order_requirement_line,
                            product_product,
                            product_template
                        WHERE order_requirement_line.order_requirement_id = order_requirement.id 
                            AND order_requirement_line.product_id = product_product.id 
                            AND product_product.product_tmpl_id = product_template.id 
                            AND NOT (order_requirement_line.id IN ( SELECT temp_mrp_bom.order_requirement_line_id
                        FROM temp_mrp_bom))) a
                  ORDER BY a.order_requirement_line_id, a.sequence
            )
            """)
