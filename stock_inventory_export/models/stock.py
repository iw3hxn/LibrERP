# -*- coding: utf-8 -*-
# © 2019 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import datetime
from xlwt import *
import logging
from cStringIO import StringIO
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
from tools.translate import _


class StockInventory(orm.Model):
    _inherit = 'stock.inventory'

    def set_header(self, ws, row):
        ws.write(row, 0, u'Codice Interno')
        ws.write(row, 1, u'Nome')
        ws.write(row, 2, u'Quantità')
        ws.write(row, 3, u'UoM')
        ws.write(row, 4, u"Prezzo d'Acquisto")
        ws.write(row, 5, u'Valore Magazzino')

    def print_inventory_costs(self, cr, uid, context):
        name = context.get('name', 'inventory')
        file_name = u'report_{0}_{1}.xls'.format(name, datetime.datetime.now().strftime('%Y-%m-%d'))

        book = Workbook(encoding='utf-8')
        # ws = book.add_sheet(name, cell_overwrite_ok=True)
        try:
            ws = book.add_sheet(name)
        except:
            ws = book.add_sheet('inventory')

        row = 0
        self.set_header(ws, row)
        row += 1

        inventory = self.browse(cr, uid, context['active_id'])

        for row, line in enumerate(inventory.inventory_line_id, row):
            # ws.write(row, 0, line.location_id.name, self.table_layout[column][style])
            ws.write(row, 0, line.product_id.default_code)
            ws.write(row, 1, line.product_id.name)
            ws.write(row, 2, line.product_qty)
            ws.write(row, 3, line.product_id.uom_id.name)
            ws.write(row, 4, line.product_id.cost_price)
            ws.write(row, 5, line.product_id.standard_price)

        file_data = StringIO()
        book.save(file_data)

        out = file_data.getvalue()
        out = out.encode("base64")
        wizard_id = self.pool['wizard.inventory.costs'].create(cr, uid, {'data': out, 'file_name': file_name}, context=context)

        view = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'stock_inventory_export', 'wizard_export_inventory_costs_form'
        )
        view_id = view and view[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Export Inventory Costs'),
            'res_model': 'wizard.inventory.costs',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'res_id': wizard_id
        }

        return True
