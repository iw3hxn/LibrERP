# -*- coding: utf-8 -*-
# © 2018 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from openerp.tools.translate import _


class ProductPricelist(orm.Model):
    _inherit = 'product.pricelist'

    _order = "name asc"

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        result = []
        for line in self.browse(cr, uid, ids, context=context):
            if line.partner_id:
                if line.type == 'sale':
                    code = line.partner_id.property_customer_ref
                else:
                    code = line.partner_id.property_supplier_ref
                name = '{0} {1}'.format(code, line.name)
                if line.partner_id.company_id.currency_id.id != line.currency_id.id:
                    name = '{0} ({1})'.format(name, line.currency_id.symbol)

                result.append((line.id, name))
            else:
                result.append((line.id, line.name))
        return result

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        pricelist_selection_ids = super(ProductPricelist, self).name_search(cr, uid, name, args, operator, context=context, limit=limit)
        if name:
            partner_ids = self.pool['res.partner'].search(cr, uid, ['|', '|', ('property_customer_ref', '=', name), ('name', 'ilike', name), ('property_supplier_ref', '=', name)], context=context)
            if partner_ids:
                if args:
                    relative_selection_ids = self.name_search(cr, uid, '', args + [('partner_id', 'in', partner_ids)], operator, context=context, limit=limit)
                else:
                    relative_selection_ids = self.name_search(cr, uid, '', [('partner_id', 'in', partner_ids)], operator, context=context, limit=limit)
                if relative_selection_ids:
                    pricelist_selection_ids = list(set(pricelist_selection_ids + relative_selection_ids))

        # Sort by name
        return sorted(pricelist_selection_ids, key=lambda x: x[1])

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        context = context or self.pool['res.users'].context_get(cr, uid)
        partner_obj = self.pool['res.partner']
        new_args = []
        for arg in args:
            if arg and len(arg) == 3 and arg[0] == 'partner_id':
                if arg[1] == '=':
                    partner_ids = partner_obj.search(cr, uid, [('id', '=', arg[2])], context=context)
                else:
                    partner_ids = partner_obj.search(cr, uid, [('name', arg[1], arg[2])], context=context)
                return_ids = []
                if partner_ids:
                    for partner in partner_obj.browse(cr, uid, partner_ids, context):
                        if partner.property_product_pricelist:
                            return_ids.append(partner.property_product_pricelist.id)
                        if partner.property_product_pricelist_purchase:
                            return_ids.append(partner.property_product_pricelist_purchase.id)
                return_ids = list(set(return_ids))
                new_args.append(('id', 'in', return_ids))
            else:
                new_args.append(arg)

        res = super(ProductPricelist, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
        return res

    # def price_rule_get_multi(self, cr, uid, ids, products_by_qty_by_partner, context=None):
    #     res = super(ProductPricelist, self).price_rule_get_multi(cr, uid, ids, products_by_qty_by_partner, context)
    #     if products_by_qty_by_partner:
    #         product = products_by_qty_by_partner[0][0]
    #         for inventory_id in ids:
    #             price, rule_id = res[product.id][inventory_id]
    #             if product.conversion:
    #                 res[product.id][inventory_id] = (price * product.conversion, rule_id)
    #             else:
    #                 res[product.id][inventory_id] = (price, rule_id)
    #     return res

    def _get_partner(self, cr, uid, ids, name, arg, context=None):
        return_res = {}
        context = context or {}

        property_field = self.pool['res.partner']._all_columns.get('property_product_pricelist').column

        def_id = self.pool['res.partner']._all_columns['property_product_pricelist'].column._field_get(cr, uid, self.pool['res.partner']._name, 'property_product_pricelist')
        company = self.pool.get('res.company')
        cid = company._company_default_get(cr, uid, self.pool['res.partner']._name, def_id, context=context)

        for product_pricelist_id in ids:
            return_res[product_pricelist_id] = {
                'partner_ids': False,
                'partner_num': 0
            }

            where_str = " WHERE " + \
                        "name = '%s' AND " % 'property_product_pricelist' + \
                        "res_id like '%s,%%' AND " % self.pool['res.partner']._name + \
                        "company_id = %s AND " % cid + \
                        "fields_id = %s AND " % def_id + \
                        "type = '%s'" % self.pool['res.partner']._all_columns['property_product_pricelist'].column._type

            args1 = [('id', '=', product_pricelist_id)]
            model_obj = self.pool.get(property_field._obj)
            model_ids = model_obj.search(cr, uid, args1, context=context)
            if model_ids:
                model_ids = map(lambda x: "'%s,%s'" % (model_obj._name, x), model_ids)
                model_ids = ",".join(model_ids)
                where_str += ' AND value_reference IN (%s)' % model_ids

            query = "SELECT res_id FROM ir_property " + where_str
            cr.execute(query)
            res = cr.fetchall()
            if res:
                res = set(res)
                res = map(lambda x: int(x[1]), [x[0].split(',') for x in res])
                return_res[product_pricelist_id] = {
                    'partner_ids': res,
                    'partner_num': len(res)
                }

        return return_res

    _columns = {
        'partner_id': fields.many2one('res.partner', string='Partner'),
        'partner_ids': fields.function(_get_partner, string='Partners', type='one2many', relation="res.partner",
                                       readonly=True, method=True, multi='get_partner'),
        'partner_num': fields.function(_get_partner, string='Partners number', type='integer', readonly=True, method=True, multi='get_partner'),

        'member_ids': fields.many2many('res.users', 'product_pricelist_rel', 'product_pricelist_id', 'member_id', 'Team Members'),
    }

    def copy(self, cr, uid, ids, default, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not default:
            default = {}
        default.update({
            'code': False,
        })
        return super(ProductPricelist, self).copy(cr, uid, ids, default, context=context)

    def _check_unique_partner(self, cr, uid, ids, context=None):
        for pricelist in self.browse(cr, uid, ids, context=context):
            if pricelist.partner_id:
                cr.execute("select id from product_pricelist where partner_id = {0}".format(pricelist.partner_id.id))
                pricelist_ids = cr.fetchall()
                if len(pricelist_ids) > 1:
                    return False
        return True

    _constraints = [(_check_unique_partner, _('Error! Exist Just another pricelist connected to partner.'), ['partner_id'])]

    def onchange_type(self, cr, uid, ids, ttype, context):
        result = {}
        warning = {}

        if ttype == 'sale':
            domain = [('customer', '=', True)]
        elif ttype == 'purchase':
            domain = [('supplier', '=', True)]
        else:
            domain = []

        domain = {
            'partner_id': domain
        }

        return {'value': result, 'domain': domain, 'warning': warning}

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(ProductPricelist, self).create(cr, uid, vals, context=context)
        if vals.get('partner_id', False) and vals.get('type', False):
            partner_vals = {}
            if vals['type'] == 'sale':
                partner_vals = {'property_product_pricelist': res}
            elif vals['type'] == 'purchase':
                partner_vals = {'property_product_pricelist_purchase': res}
            if partner_vals:
                self.pool['res.partner'].write(cr, uid, vals.get('partner_id'), partner_vals, context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(ProductPricelist, self).write(cr, uid, ids, vals, context=context)
        if vals.get('partner_id', False):
            for pricelist in self.browse(cr, uid, ids, context=context):
                partner_vals = {}
                if pricelist['type'] == 'sale':
                    partner_vals = {'property_product_pricelist': pricelist.id}
                elif pricelist['type'] == 'purchase':
                    partner_vals = {'property_product_pricelist_purchase': pricelist.id}
                if partner_vals:
                    self.pool['res.partner'].write(cr, uid, vals.get('partner_id'), partner_vals, context)
        return res
