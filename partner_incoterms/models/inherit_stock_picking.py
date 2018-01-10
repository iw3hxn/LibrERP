# -*- encoding: utf-8 -*-
##############################################################################
#

from openerp.osv import orm, fields


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterm'),
    }
