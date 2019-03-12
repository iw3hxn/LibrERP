# -*- coding: utf-8 -*-
# © 2019 Carlo Vettore - Didotech srl (www.didotech.com)

import platform

from openerp.osv import orm, fields


class CompanyConfig(orm.Model):
    _inherit = "res.company"

    def _get_node(self, cr, uid, ids, field_name, arg, context):
        node = platform.node()
        return {company_id: node for company_id in ids}

    _columns = {
        'email_node': fields.char('Node', 64, required=True),
        'local_node': fields.function(_get_node, string='Node', method=True, type="char")
    }

