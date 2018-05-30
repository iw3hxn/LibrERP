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
