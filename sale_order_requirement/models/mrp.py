# -*- coding: utf-8 -*-
# © 2017 Antonio Mignolli - Didotech srl (www.didotech.com)

from osv import fields, orm
from tools.translate import _


class mrp_bom(orm.Model):
    _inherit = 'mrp.bom'

    _index_name = 'mrp_bom_product_id_index'

    def _auto_init(self, cr, context={}):
        super(mrp_bom, self)._auto_init(cr, context)
        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s',
                   (self._index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON mrp_bom (product_id)'.format(name=self._index_name))

    def _child_compute_buy_and_produce(self, cr, uid, ids, name, arg, context=None):
        result = {}
        if context is None:
            context = {}
        bom_model = self.pool['mrp.bom']
        bom_id = context and context.get('active_id', False) or False
        cr.execute('select id from mrp_bom')
        if all(bom_id != r[0] for r in cr.fetchall()):
            ids.sort()
            bom_id = ids[0]
        bom_parent = bom_model.browse(cr, uid, bom_id, context=context)
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
                sids = bom_model.search(cr, uid, [('bom_id', '=', False),
                                                  ('product_id', '=', bom.product_id.id)])
                if sids:
                    bom2 = bom_model.browse(cr, uid, sids[0], context=context)
                    result[bom.id] += map(lambda x: x.id, bom2.bom_lines)

        return result

    _columns = {
        'child_buy_and_produce_ids': fields.function(_child_compute_buy_and_produce, relation='mrp.bom',
                                                     string="BoM Hierarchy", type='many2many'),
        'product_type': fields.related('product_id', 'type', type='selection', string='Product Type', selection=[('product', 'Stockable Product'), ('consu', 'Consumable'), ('service', 'Service')]),
    }

    def view_open_product(self, cr, uid, ids, context):
        mrp_boms = self.browse(cr, uid, ids, context)
        res = self.pool['ir.model.data'].get_object_reference(cr, uid, 'product', 'product_normal_form_view')

        vals = {
            'type': 'ir.actions.act_window',
            'name': _('Product'),
            'view_type': 'form',
            'view_mode': 'page',
            'view_id': res and res[1] or False,
            'res_model': 'product.product',
            'nodestroy': True,
            'target': 'inline',
            'res_id': mrp_boms and mrp_boms[0].product_id.id
        }

        return vals
