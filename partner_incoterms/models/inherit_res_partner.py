# -*- encoding: utf-8 -*-
##############################################################################

from openerp.osv import orm, fields


class res_partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'default_incoterm_id': fields.many2one('stock.incoterms', 'Default Incoterm', help='Default Incoterm used in a Purchase Order when this partner is selected as the supplier.'),
    }
