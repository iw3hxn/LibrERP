# -*- encoding: utf-8 -*-
from tools.translate import _
import netsvc as netsvc
from openerp.osv import fields, orm


class res_partner_inherit(orm.Model):

    _inherit = 'res.partner'

    _columns = {
        'mgmtsystem_nonconformity_ids': fields.one2many('mgmtsystem.nonconformity', 'partner_id', 'Non conformity',
                                                        readonly=True),
    }

    # def button_dummy(self, cr, uid, ids, context=None):
    #     from pprint import pprint
    #     for p in self.browse(cr, uid, ids, context):
    #         ncs = [n.description for n in p.mgmtsystem_nonconformity_ids]
    #         pprint(ncs)
