# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from osv import osv, fields, orm


class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'

    def _child_compute_buy_and_produce(self, cr, uid, ids, name, arg, context=None):
        result = {}
        if context is None:
            context = {}
        bom_obj = self.pool.get('mrp.bom')
        bom_id = context and context.get('active_id', False) or False
        cr.execute('select id from mrp_bom')
        if all(bom_id != r[0] for r in cr.fetchall()):
            ids.sort()
            bom_id = ids[0]
        bom_parent = bom_obj.browse(cr, uid, bom_id, context=context)
        for bom in self.browse(cr, uid, ids, context=context):
            if bom_parent or (bom.id == bom_id):
                result[bom.id] = map(lambda x: x.id, bom.bom_lines)
            else:
                result[bom.id] = []
            if bom.bom_lines:
                continue
            ok = name == 'child_buy_and_produce_ids' and (bom.product_id.supply_method in ('buy', 'produce'))
            # Changed from inherited -> is GOOD ALSO bom.type=='buy',
            # it was -> and (bom.product_id.supply_method=='produce'))
            if bom.type == 'phantom' or ok:
                sids = bom_obj.search(cr, uid, [('bom_id', '=', False),
                                                ('product_id', '=', bom.product_id.id)])
                if sids:
                    bom2 = bom_obj.browse(cr, uid, sids[0], context=context)
                    result[bom.id] += map(lambda x: x.id, bom2.bom_lines)

        return result

    _columns = {
        'child_buy_and_produce_ids': fields.function(_child_compute_buy_and_produce, relation='mrp.bom',
                                                     string="BoM Hierarchy", type='many2many'),
    }

    # NOT USED ANYMORE
    # @staticmethod
    # def get_all_mrp_bom_children(obj, level=0):
    #     result = {}
    #
    #     def _get_rec(obj, level):
    #         for l in obj:
    #             res = {'name': l.name,
    #                    'pname': l.product_id.name,
    #                    'pcode': l.product_id.default_code,
    #                    'pqty': l.product_qty,
    #                    'uname': l.product_uom.name,
    #                    'code': l.code,
    #                    'level': level
    #                    }
    #
    #             result[l.id] = res
    #             if l.child_buy_and_produce_ids:
    #                 if level < 6:
    #                     level += 1
    #                 _get_rec(l.child_buy_and_produce_ids, level)
    #                 if 0 < level < 6:
    #                     level -= 1
    #         return result
    #
    #     children = _get_rec(obj, level)
    #
    #     return children
