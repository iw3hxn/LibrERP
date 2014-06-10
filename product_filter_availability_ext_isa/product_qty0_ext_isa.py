# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 ISA s.r.l. (<http://www.isa.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from tools.translate import _


class product_qty0_ext_isa(osv.osv):
    
    _description = "Product extension for filter qty=0"
    _inherit = 'product.product'
    
    def search(self, cr, uid, args, offset=0, limit=None,
                order=None, context=None, count=False):
        #~ import pdb; pdb.set_trace()
        res = []
        if context is None:
            context = {}
        if not context.has_key('not0'):
            res = super(product_qty0_ext_isa, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)
                
        else:
            #~ import pdb; pdb.set_trace()
            res=self._search_available(cr, uid, args, offset, limit,
                order, context, count)
        return res
        
    def _search_available(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        
        if context is None:
            context = {}
        #TODO: verificare se queste condizioni sono tutte necessarie
        if context.get('shop', False):
            cr.execute('select warehouse_id from sale_shop where id=%s', (int(context['shop']),))
            res2 = cr.fetchone()
            if res2:
                context['warehouse'] = res2[0]

        if context.get('warehouse', False):
            cr.execute('select lot_stock_id from stock_warehouse where id=%s', (int(context['warehouse']),))
            res2 = cr.fetchone()
            if res2:
                context['location'] = res2[0]

        if context.get('location', False):
            if type(context['location']) == type(1):
                location_ids = [context['location']]
            elif type(context['location']) in (type(''), type(u'')):
                location_ids = self.pool.get('stock.location').search(cr, user, [('name','ilike',context['location'])], context=context)
            else:
                location_ids = context['location']
        else:
            location_ids = []
            wids = self.pool.get('stock.warehouse').search(cr, user, [], context=context)
            for w in self.pool.get('stock.warehouse').browse(cr, user, wids, context=context):
                location_ids.append(w.lot_stock_id.id)

        # build the list of ids of children of the location given by id
        if context.get('compute_child',True):
            child_location_ids = self.pool.get('stock.location').search(cr, user, [('location_id', 'child_of', location_ids)])
            location_ids = child_location_ids or location_ids
        else:
            location_ids = location_ids
        #~ import pdb; pdb.set_trace()
        #self.pool.get('ir.model.access').check(cr, access_rights_uid or user, self._name, 'read', context=context)
        select="""
                    select stock_move.product_id
                    from %s
                    ,stock_move
              """   
        where="""
                    where stock_move.product_id=product_product.id and stock_move.location_id NOT IN (%s) and stock_move.location_dest_id IN (%s)
                    and stock_move.state IN ('confirmed', 'done') 
              """
        group="""        
                    group by stock_move.product_id,stock_move.product_uom
              """
        having="""      
                    HAVING (sum(stock_move.product_qty)-(
                        select coalesce(sum(stock_move_b.product_qty),0)
                        from stock_move stock_move_b
                        where stock_move_b.location_id IN (%s) and stock_move_b.location_dest_id NOT IN (%s)
                        and stock_move_b.product_id=stock_move.product_id
                        and stock_move_b.state in ('confirmed', 'done'))
                    ) > 0
               """ 
        query = self._where_calc(cr, user, args, context=context)
        #TODO: verificare
        self._apply_ir_rules(cr, user, query, 'read', context=context)
        #il _generate_order_by va prima del get_sql altrimenti non aggiorna la from_clause
        locations=''
        sep=''
        for loc in location_ids:
            locations=sep+str(loc)
            sep=','
        order_by = self._generate_order_by(order, query)
        from_clause, where_clause, where_clause_params = query.get_sql()
        limit_str = limit and ' limit %d' % limit or ''
        offset_str = offset and ' offset %d' % offset or ''             
        add_where_str = where_clause and " and %s" % where_clause or ''
        where=where % (locations,locations)
        where+=add_where_str
        having=having % (locations,locations)
        #FIXME: servono i campi con i quali si fa l'ordinamento da mettere nel group by... per ora li prendo dall'order
        add_group_by=order_by.replace("ORDER BY","").replace("asc","").replace("desc","")
        group+= add_group_by and ','+add_group_by
        query_str=(select % from_clause)+where+group+having+order_by+limit_str+offset_str
        #~ import pdb; pdb.set_trace()
        cr.execute(query_str,where_clause_params)
        res = cr.fetchall()
        return [x[0] for x in res]
            
        
product_qty0_ext_isa()
    
    
