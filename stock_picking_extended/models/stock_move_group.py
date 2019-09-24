# -*- coding: utf-8 -*-
import logging

import decimal_precision as dp
import tools
from openerp.osv import fields, orm

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class StockMoveGroup(orm.Model):
    _name = 'stock.move.group'

    _auto = False
    _rec_name = 'product_id'

    _columns = {
        'year': fields.integer('Year'),
        'document_date': fields.datetime('Date'),
        'real_date': fields.date('Real Date'),
        'stock_journal_id': fields.many2one('stock.journal', 'Journal'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'product_id': fields.many2one('product.product', 'Product'),
        'categ_id': fields.many2one('product.category', 'Category'),
        'location_id': fields.many2one('stock.location', 'Location'),
        'qty_out': fields.float(string='Out Qty', digits_compute=dp.get_precision('Product UoM')),
        'qty_in': fields.float(string='In Qty', digits_compute=dp.get_precision('Product UoM')),
        'product_qty': fields.float(string='Qty', digits_compute=dp.get_precision('Product UoM')),
        'product_uom': fields.many2one('product.uom', 'Product Uom'),
        'price': fields.float(string='Price Unit', digits_compute=dp.get_precision('Sale Price')),
        'origin': fields.char('Origin', size=64),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'source_location_id': fields.reference("Source Location", [
            ('sale.order', 'Sale Order'),
            ('pos.order', 'Pos Order'),
            ('purchase.order', 'Purchase Order')], size=128),
        'stock_balance': fields.float(string='Product Qty on Hand', digits_compute=dp.get_precision('Product UoM')),
        'move_value': fields.float(string='Move Price', digits_compute=dp.get_precision('Purchase Price')),
        'average': fields.float(string='Average Price', digits_compute=dp.get_precision('Purchase Price')),
        'average_year': fields.float(string='Average Price Year', digits_compute=dp.get_precision('Purchase Price')),
        'location_amount': fields.float(string='Location Amount', digits_compute=dp.get_precision('Purchase Price')),
        'location_amount_year': fields.float(string='Location Amount Year', digits_compute=dp.get_precision('Purchase Price')),
        'move_line_id': fields.many2one('stock.move', 'Move', readonly=True),
    }

    _order = "document_date, id"

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'stock_move_group')
        try:
            cr.execute("""
                create or replace view stock_move_group AS (
                SELECT 
                    D.*,
                    average * stock_balance AS location_amount,
                    average_year * stock_balance AS location_amount_year,
                    pt.categ_id
                FROM(
                    SELECT
                        to_char(C.document_date, 'MM') as month,
                        date_trunc('day', C.document_date)::DATE AS real_date,
                        *,                                       
                        CASE
                            WHEN sum_product_qty != 0
                            THEN sum_move_value / sum_product_qty
                            ELSE 0
                        END AS average,
                        CASE
                            WHEN sum_product_qty_year != 0
                                THEN sum_move_value_year / sum_product_qty_year
                            ELSE 0
                        END AS average_year,
                        CASE
                            WHEN qty_in > 0
                                THEN qty_in
                            WHEN qty_out > 0
                                THEN -qty_out
                            ELSE 0
                        END AS product_qty
                        
                        FROM (
                            SELECT *, 
                            SUM(qty_in - qty_out) OVER (PARTITION by product_id, location_id ORDER by document_date, id) AS stock_balance,
                            SUM(case when purchase_id is not Null and partner_id != 1 THEN move_value ELSE 0 END) OVER (PARTITION BY product_id, location_id ORDER by document_date, id) AS sum_move_value,
                            SUM(case when purchase_id is not Null and partner_id != 1 THEN qty_in ELSE 0 END) OVER (PARTITION BY product_id, location_id ORDER by document_date, id) AS sum_product_qty,
                            SUM(case when purchase_id is not Null and partner_id != 1 THEN move_value ELSE 0 END) OVER (PARTITION BY product_id, location_id, year ORDER by document_date, id) AS sum_move_value_year,
                            SUM(case when purchase_id is not Null and partner_id != 1 THEN qty_in ELSE 0 END) OVER (PARTITION BY product_id, location_id, year ORDER by document_date, id) AS sum_product_qty_year
                        
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
                                qty_in AS qty_in,
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
                                END AS source_location_id,
                                
                                CASE
                                    WHEN qty_in > 0
                                        THEN qty_in * price
                                    ELSE 0
                                END AS move_value,
                                purchase_id AS purchase_id                             
                                
                                FROM (
                                    SELECT 	sm.create_date AS move_line_create,
                                            sm.date AS document_date,
                                            sm.partner_id as partner_id, 
                                            sp.stock_journal_id AS stock_journal_id, 
                                            sm.product_id AS product_id,
                                            sm.location_id AS location_id,
                                            0 AS qty_in,
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
                                            sm.location_id in (SELECT id FROM stock_location WHERE usage='internal')
                                            
                                    UNION ALL
                                    
                                    SELECT 	sm.create_date AS move_line_create,
                                            sm.date AS document_date,
                                            sm.partner_id as partner_id,
                                            Null AS stock_journal_id, 
                                            sm.product_id AS product_id,
                                            sm.location_id AS location_id,
                                            0 AS qty_in,
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
                                            sm.location_id in (SELECT id FROM stock_location WHERE usage='internal')
                                    
                                    UNION ALL
                                    
                                    SELECT 	sm.create_date AS move_line_create,                                            
                                            sm.date AS document_date,
                                            sm.partner_id as partner_id,
                                            sp.stock_journal_id AS stock_journal_id, 
                                            sm.product_id AS product_id,
                                            sm.location_dest_id AS location_id,
                                            sm.product_qty AS qty_in, 
                                            0 AS qty_out,
                                            sm.product_uom AS product_uom, 
                                            sm.price_unit AS price,
                                            sp.origin AS origin,
                                            sp.sale_id AS sale_id,
                                            sp.purchase_id AS purchase_id,
                                            sm.id AS move_line_id,
                                            sm.picking_id AS picking_id
                                    FROM    stock_move AS sm, 
                                            stock_picking AS sp
                                    WHERE   sm.state = 'done' and sm.picking_id = sp.id and
                                            sm.location_dest_id in (SELECT id FROM stock_location WHERE usage='internal')
                                            
                                    UNION ALL
                                    
                                    SELECT 	sm.create_date AS move_line_create,
                                            sm.date AS document_date,
                                            sm.partner_id as partner_id,
                                            Null AS stock_journal_id, 
                                            sm.product_id AS product_id,
                                            sm.location_dest_id AS location_id,
                                            sm.product_qty AS qty_in,
                                            0 AS qty_out, 
                                            sm.product_uom AS product_uom, 
                                            sm.price_unit AS price,
                                            sm.name as origin,
                                            Null AS sale_id,
                                            Null AS purchase_id ,
                                            sm.id AS move_line_id,
                                            sm.picking_id AS picking_id
                                    FROM    stock_move AS sm
                                    WHERE   sm.state = 'done' AND sm.picking_id is Null AND
                                            sm.location_dest_id in (SELECT id FROM stock_location WHERE usage='internal')
                                    
                                    ) AS A
                                    ORDER BY document_date
                        ) AS B
                        ) AS C
                        ) as D, product_template as pt , product_product as pp 
                    WHERE pp.product_tmpl_id = pt.id AND pp.id = D.product_id 
                        
                )                 
                
            """)
        except Exception as e:
            _logger.error(u'Error: {error}'.format(error=e))


