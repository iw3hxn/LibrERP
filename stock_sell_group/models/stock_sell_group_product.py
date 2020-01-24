# -*- coding: utf-8 -*-
import logging

import decimal_precision as dp
import tools
from openerp.osv import fields, orm

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class StockSellGroupProduct(orm.Model):
    _name = 'stock.sell.group.product'

    _auto = False
    _rec_name = 'product_id'

    _columns = {
        'year': fields.integer('Year'),
        'product_id': fields.many2one('product.product', 'Product'),
        'categ_id': fields.many2one('product.category', 'Category'),
        'location_id': fields.many2one('stock.location', 'Location'),
        'qty_out': fields.float(string='Out Qty', digits_compute=dp.get_precision('Product UoM')),
        'default_code': fields.char('Default Code', size=64),
    }

    _order = "qty_out desc, id"

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'stock_sell_group_product')
        try:
            cr.execute("""
                create or replace view stock_sell_group_product AS (
                SELECT F.* 
                    FROM(
            
                    SELECT 
                        E.year, 
                        E.product_id, 
                        E.location_id, 
                        E.categ_id,
                        E.default_code,
                        sum(E.qty_out) AS qty_out, 
                        min(E.id) as ID
                    FROM(
                    SELECT 
                                D.*,
                                pt.categ_id,
                    pp.default_code
                    
                    FROM(
                    SELECT
                        to_char(B.document_date, 'MM') as month,
                        date_trunc('day', B.document_date)::DATE AS real_date,
                        *                    
                        FROM (
                            SELECT 
                                row_number() OVER ()::INTEGER AS id, 
                                document_date AS document_date,
                                to_char(document_date, 'YYYY'::text)::INTEGER AS year,
                                partner_id AS partner_id,
                                stock_journal_id AS stock_journal_id,
                                product_id AS product_id,
                                location_id AS location_id,
                                qty_out AS qty_out,
                                product_uom AS product_uom,
                                price AS price,
                                origin AS origin,
                                move_line_id AS move_line_id,
                                CASE
                                    WHEN purchase_id is not Null
                                        THEN concat('purchase.order,', purchase_id)
                                    WHEN sale_id is not Null
                                        THEN concat('sale.order,', sale_id)
                                    WHEN picking_id is not Null
                                        THEN concat('stock.picking,', picking_id)
                                    ELSE Null
                                END AS source_location_id
                                                                
                                FROM (
                                    SELECT 	sm.create_date AS move_line_create,
                                            sm.date AS document_date,
                                            sm.partner_id as partner_id, 
                                            sp.stock_journal_id AS stock_journal_id, 
                                            sm.product_id AS product_id,
                                            sm.location_id AS location_id,
                                            sm.product_qty AS qty_out, 
                                            sm.product_uom AS product_uom, 
                                            sm.price_unit AS price,
                                            sp.origin AS origin,
                                            sp.sale_id AS sale_id,
                                            sp.purchase_id AS purchase_id, 
                                            sm.id AS move_line_id,
                                            sm.picking_id AS picking_id
                                    FROM    stock_move AS sm, 
                                            stock_picking AS sp
                                    WHERE   sm.state = 'done' and sm.picking_id = sp.id AND
                                            sm.location_id in (SELECT id FROM stock_location WHERE usage='internal') AND
                                            sm.location_dest_id in (SELECT id FROM stock_location WHERE usage='customer')
                                    UNION ALL
                                    
                                    SELECT 	sm.create_date AS move_line_create,
                                            sm.date AS document_date,
                                            sm.partner_id as partner_id, 
                                            sp.stock_journal_id AS stock_journal_id, 
                                            sm.product_id AS product_id,
                                            sm.location_dest_id AS location_id,
                                            - sm.product_qty AS qty_out, 
                                            sm.product_uom AS product_uom, 
                                            sm.price_unit AS price,
                                            sp.origin AS origin,
                                            sp.sale_id AS sale_id,
                                            sp.purchase_id AS purchase_id, 
                                            sm.id AS move_line_id,
                                            sm.picking_id AS picking_id
                                    FROM    stock_move AS sm, 
                                            stock_picking AS sp
                                    WHERE   sm.state = 'done' and sm.picking_id = sp.id AND
                                            sm.location_dest_id in (SELECT id FROM stock_location WHERE usage='internal') AND
                                            sm.location_id in (SELECT id FROM stock_location WHERE usage='customer')
                                    UNION ALL
                                    
                                    SELECT 	sm.create_date AS move_line_create,
                                            sm.date AS document_date,
                                            sm.partner_id as partner_id,
                                            Null AS stock_journal_id, 
                                            sm.product_id AS product_id,
                                            sm.location_id AS location_id,
                                            sm.product_qty AS qty_out, 
                                            sm.product_uom AS product_uom, 
                                            sm.price_unit AS price,
                                            sm.name as origin,
                                            Null AS sale_id,
                                            Null AS purchase_id,
                                            sm.id AS move_line_id,
                                            sm.picking_id AS picking_id
                                    FROM    stock_move AS sm
                                    WHERE   sm.state = 'done' and sm.picking_id is Null AND
                                            sm.location_id in (SELECT id FROM stock_location WHERE usage='internal') AND
                                            sm.location_dest_id in (SELECT id FROM stock_location WHERE usage='customer')
                                    ) AS A
                                    ORDER BY document_date
                        ) AS B
                        ) AS D, product_template AS pt , product_product AS pp
                    WHERE pp.product_tmpl_id = pt.id AND pp.id = D.product_id) AS E GROUP BY year, product_id, location_id, categ_id, default_code) AS F ORDER BY qty_out desc
                
                )                 
                
            """)
        except Exception as e:
            _logger.error(u'Error: {error}'.format(error=e))


