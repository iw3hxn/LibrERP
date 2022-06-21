# -*- coding: utf-8 -*-

from openerp.osv import orm


class ResPartner(orm.Model):

    _inherit = 'res.partner'

    def name_get(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(ResPartner, self).name_get(cr, uid, ids, context)
        if context.get('supplier_warning'):
            warning = {}
            for partner in self.browse(cr, uid, ids, context):
                warning[partner.id] = partner.purchase_warn != 'no-message'

            new_res = []
            for element in res:
                name = u"[!] {}".format(element[1]) if warning[element[0]] else element[1]
                new_res.append((element[0], name))

            res = new_res
        return res
