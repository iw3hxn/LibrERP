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

    _columns = {
        'level': fields.integer("Level"),
        'level_name': fields.char('Level Name'),
        'product_id': fields.many2one('product.product', 'Original Product', readonly=True),
        'order_requirement_id': fields.many2one('order.requirement', 'Order Reference'),
        'supplier_id': fields.many2one('res.partner', 'Supplier', readonly=True,
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



    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'full_order_requirement_line')

        cr.execute("""
            CREATE or REPLACE view full_order_requirement_line AS (
                SELECT * FROM (
                    SELECT 
                        temp_mrp_bom.bom_id as bom_parent_id,
                        temp_mrp_bom.id as bom_id,
                        temp_mrp_bom.level_name as level_name,
                        temp_mrp_bom.sequence * 100000 + temp_mrp_bom.order_requirement_line_id as id,
                        temp_mrp_bom.level AS level,
                        temp_mrp_bom.product_id AS product_id,
                        
                        order_requirement.id AS order_requirement_id,
                        temp_mrp_bom.supplier_id AS supplier_id,
                        temp_mrp_bom.product_qty AS qty,
                        temp_mrp_bom.product_uom AS product_uom,
                        temp_mrp_bom.user_id AS user_id,
                        temp_mrp_bom.state AS state,
                        temp_mrp_bom.buy AS buy,
                        temp_mrp_bom.is_manufactured AS is_manufactured,
                        product_template.categ_id AS categ_id,
                        temp_mrp_bom.order_requirement_line_id AS order_requirement_line_id,
                        temp_mrp_bom.sequence AS sequence
                     FROM
                        order_requirement,
                        order_requirement_line,
                        temp_mrp_bom,
                        product_product,
                        product_template
                    WHERE
                        temp_mrp_bom.order_requirement_line_id = order_requirement_line.id 
                        AND order_requirement_line.order_requirement_id = order_requirement.id
                        AND temp_mrp_bom.product_id = product_product.id
                        AND product_product.product_tmpl_id = product_template.id
                        AND temp_mrp_bom.active = 'True'
              
    
                    UNION
                    
                    SELECT 
                        0 AS bom_parent_id,
                        0 AS bom_id,
                        '' AS level_name,
                        order_requirement_line.id AS id,
                        0 AS level,
                        order_requirement_line.product_id AS product_id,
                        order_requirement.id AS order_requirement_id,
                        order_requirement_line.supplier_id AS supplier_id,
                        order_requirement_line.qty AS qty,
                        product_template.uom_id AS product_uom,
                        order_requirement_line.user_id AS user_id,
                        order_requirement_line.state AS state,
                        order_requirement_line.buy AS buy,
                        order_requirement_line.is_manufactured AS is_manufactured,
                        product_template.categ_id AS categ_id,
                        order_requirement_line.id AS order_requirement_line_id,
                        order_requirement_line.id AS sequence
                        
                        FROM
                            order_requirement,
                            order_requirement_line,
                            product_product,
                            product_template
                        WHERE
                            order_requirement_line.order_requirement_id = order_requirement.id
                            AND order_requirement_line.product_id = product_product.id
                            AND product_product.product_tmpl_id = product_template.id
                            AND order_requirement_line.id not in (select order_requirement_line_id from temp_mrp_bom)
                    
                    ) AS A
                    ORDER BY order_requirement_line_id, sequence            
                
                );
            """)
