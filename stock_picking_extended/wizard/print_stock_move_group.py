# -*- coding: utf-8 -*-

from openerp.osv import orm, fields

from openerp.tools.translate import _
from datetime import datetime


class PrintStockMoveGroup(orm.TransientModel):
    _name = "print.stock.move.group"

    _columns = {
        'name': fields.char('Name'),
        'date_from': fields.date('Date From', required=True),
        'date_to': fields.date('Date To', required=True),
        'product_id': fields.many2one('product.product', 'Product', domain="[('type', '!=', 'service')]"),
        'location_id': fields.many2one('stock.location', 'Location', domain="[('usage', '=', 'internal')]", required=1),
        'show_partner': fields.boolean('Show Partner'),
        'show_journal': fields.boolean('Show Journal')
    }

    _defaults = {
        'name': _('Print Stock Move Group'),
        'date_from': lambda *a: datetime.now().strftime("%Y-01-01"),
        'date_to': lambda *a: datetime.now().strftime("%Y-12-31")
    }

    def action_print(self, cr, uid, ids, context):

        wizard = self.browse(cr, uid, ids[0], context)
        stock_move_group_obj = self.pool['stock.move.group']
        domain = [('real_date', '>', wizard.date_from), ('real_date', '<', wizard.date_to)]
        if wizard.product_id:
            domain.append(('product_id', '=', wizard.product_id.id))
        if wizard.location_id:
            domain.append(('location_id', '=', wizard.location_id.id))

        move_groups_ids = stock_move_group_obj.search(cr, uid, domain, context=context)
        # move_groups = stock_move_group_obj.browse(cr, uid, move_groups_ids, context)

        ctx = {
            'show_partner': wizard.show_partner,
            'show_journal': wizard.show_journal,
            'move_groups': move_groups_ids,
            'location_name': wizard.location_id.name
        }
        return self.pool['account.invoice'].print_report(cr, uid, ids, 'stock_picking_extended.report_stock_move_group', ctx)
