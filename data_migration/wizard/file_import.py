# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014-2018 Didotech SRL (info at didotech.com)
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import base64

from openerp.addons.data_migration.utils import bom_importer
from openerp.addons.data_migration.utils import crm_importer
from openerp.addons.data_migration.utils import inventory_importer
from openerp.addons.data_migration.utils import invoice_importer
from openerp.addons.data_migration.utils import partner_importer
from openerp.addons.data_migration.utils import picking_importer
from openerp.addons.data_migration.utils import pricelist_importer
from openerp.addons.data_migration.utils import product_importer
from openerp.addons.data_migration.utils import sales_importer
from openerp.osv import orm, fields
from tools.translate import _


class filedata_import(orm.TransientModel):
    _name = "filedata.import"
    _inherit = "ir.wizard.screen"

    # # # # # # # # # # # # # #
    # action of button click  #
    # # # # # # # # # # # # # #
    def actionCheckEncoding(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid, context=context)

        # WARNING: Context is required, for correct functionally of 'read'.
        record = self.browse(cr, uid, ids[0], context=context)

        # Extration file content, encoded in base64
        contentBase64 = record.content_base64

        # Check if user supplied the data,
        # if data was not supplied show a message
        if not contentBase64:
            # Send a message to the user telling that there is a missing field
            raise orm.except_orm(
                'Attenzione!',
                'Non è stato selezionato il file da importare'
            )
        # Decoding content of file and store the resulting text in object
        decodedText = base64.decodestring(contentBase64)

        vals = {
            'content_text': decodedText,
            'file_name': record.file_name,
        }
        self.write(cr, uid, ids, vals, context=context)

        self.actionStartImport(cr, uid, ids, context)
        return False

    def actionStartImport(self, cr, uid, ids, context=False):
        # Set 'end' as a next state
        self.write(cr, uid, ids, {'state': 'end'}, context=context)

        # for OE 6.1; memory object not move data in other thread - move data
        # in parameters
        cr.commit()
        # Start import
        data_importer = self.importer.ImportFile(cr, uid, ids, context)
        data_importer.start()
        return False


class partner_import(filedata_import):
    _name = "partner.import"
    _description = "Import partner from a file in .xls format."

    importer = partner_importer

    # data fields on DB table
    _columns = {
        # State of this wizard
        'state': fields.selection(
            (
                ('import', 'import'),
                ('end', 'end')
            ), 'state', required=True, translate=False, readonly=True
        ),
        'format': fields.selection(
            (
                ('FormatOne', _('Format One')),
                ('FormatTwo', _('Format Two')),
                ('FormatThree', _('Format Three')),
                ('FormatFour', _('Format Four')),
                ('FormatFive', _('Format Five')),
                ('FormatOmnitron', _('Format Omnitron')),
            ), 'Formato Dati', required=True, readonly=False
        ),
        # file name of import
        'file_name': fields.char('Nome File', size=256),
        # Data of file, in code BASE64
        'content_base64': fields.binary(
            'Partner file path', required=True, translate=False
        ),
        # Data of file, in code text
        'content_text': fields.binary('File Partner', translate=False),
        'progress_indicator': fields.integer(
            'Progress import ', size=3, translate=False, readonly=True
        ),
        'partner_type': fields.selection(
            (
                ('customer', 'Customer'),
                ('supplier', 'Supplier')
            ), 'Partner Type', required=True
        ),
        'strict': fields.boolean(
            'Strict', help="Use more strict (and more slow) data check"
        ),
        'update_on_code': fields.boolean(
            'Update Partner by Code', help="Update Partner based on code"
        ),
        'partner_template_id': fields.many2one(
            'partner.import.template', 'Partner Import Template'
        ),
    }
    # default value for data fields of object
    _defaults = {
        'state': 'import',
        'progress_indicator': 0,
        'strict': False
    }


class product_import(filedata_import):
    _name = "product.import"
    _description = "Import products from file in .csv format."

    importer = product_importer

    # data fields on DB table
    _columns = {
        # State of this wizard
        'state': fields.selection(
            (
                ('import', 'import'),
                ('preview', 'preview'),
                ('end', 'end')
            ), 'state', required=True, translate=False, readonly=True
        ),
        'format': fields.selection(
            (
                ('FormatOne', _('Format One')),
                ('FormatTwo', _('Format Two')),
                ('FormatThree', _('Format Three')),
                ('FormatFour', _('Format Four')),
                ('FormatFive', _('Format Five')),
                ('FormatSix', _('Format Six')),
                ('FormatOmnitron', _('Format Omnitron')),
                ('FormatStandardPriceUpdate', _('Update Standard Price'))
            ), 'Formato Dati', required=True, readonly=False
        ),
        # Data of file, in code BASE64
        'content_base64': fields.binary(
            'Products file path', required=False, translate=False
        ),
        'file_name': fields.char('File Name', size=256),
        # Data of file, in code text
        'content_text': fields.binary(
            'File Partner', required=False, translate=False
        ),
        # Codecs
        # 'text_encoding': fields.selection(
        #     [
        #         (ASCII_CODE, 'ascii'),
        #         (ISO_8859_15_CODE, 'iso-8859-15'),
        #         ('utf-8',  'Unicode 8')
        #     ], 'Text encoding', required=True, translate=False
        # ),
        # problem's row of product. original code
        'preview_text_original': fields.binary(
            'Preview text original', required=False,
            translate=False, readonly=True
        ),
        # problem's row of product. decoded
        'preview_text_decoded': fields.text(
            'Preview text decoded', required=False,
            translate=False, readonly=True
        ),
        # Supplier
        # 'supplier': fields.many2one(
        #    'res.partner', 'Seller', required=True, translate=False
        # ),
        'progress_indicator': fields.integer(
            'Progress import ', size=3, translate=False, readonly=True
        ),
        # 'file_path': fields.char('Percorso file', size=256)
        'update_product_name': fields.boolean(
            'Update Product Name', help="If set, overwrite product name"
        ),
        'update_only': fields.boolean(
            'Update Only', help="If set, only existing products will be updated. New products will be not created"
        )
    }
    # default value for data fields of object
    _defaults = {
        # 'text_encoding': ISO_8859_15_CODE,
        'state': 'import',
        'progress_indicator': 0,
    }


class picking_import(filedata_import):
    _name = "picking.import"
    _description = "Import picking from file in .csv format."

    importer = picking_importer

    # data fields on DB table
    _columns = {
        # State of this wizard
        'state': fields.selection(
            (
                ('import', 'import'),
                ('preview', 'preview'),
                ('end', 'end')
            ), 'state', required=True, translate=False, readonly=True
        ),
        'format': fields.selection(
            (
                ('FormatOne', _('Format One')),
                ('FormatTwo', _('Format Two')),
            ), 'Formato Dati', required=True, readonly=False
        ),
        'address_id': fields.many2one(
            'res.partner.address', 'Address',
            help="Address of partner", required=True
        ),
        'stock_journal_id': fields.many2one(
            'stock.journal', 'Stock Journal',
            select=True, required=True
        ),
        'location_id': fields.many2one(
            'stock.location', 'Location',
            select=True, required=True,
            domain="[('usage', '!=', 'view')]"
        ),
        'location_dest_id': fields.many2one(
            'stock.location', 'Dest. Location',
            select=True, required=True,
            domain="[('usage', '!=', 'view')]"
        ),

        # Data of file, in code BASE64
        'content_base64': fields.binary(
            'Picking file path', required=False, translate=False
        ),
        'file_name': fields.char('File Name', size=256),
        # Data of file, in code text
        'content_text': fields.binary(
            'File Partner', required=False, translate=False
        ),
        # Codecs
        # 'text_encoding': fields.selection(
        #     [
        #         (ASCII_CODE, 'ascii'),
        #         (ISO_8859_15_CODE, 'iso-8859-15'),
        #         ('utf-8', 'Unicode 8')
        #     ], 'Text encoding', required=True, translate=False
        # ),
        # problem's row of product. original code
        'preview_text_original': fields.binary(
            'Preview text original', required=False,
            translate=False, readonly=True
        ),
        # problem's row of product. decoded
        'preview_text_decoded': fields.text(
            'Preview text decoded', required=False,
            translate=False, readonly=True
        ),
        # Supplier
        # 'supplier': fields.many2one(
        #     'res.partner', 'Seller', required=True, translate=False
        # ),
        'progress_indicator': fields.integer(
            'Progress import ', size=3, translate=False, readonly=True
        ),
        # 'file_path': fields.char('Percorso file', size=256)
    }
    # default value for data fields of object
    _defaults = {
        # 'text_encoding': ISO_8859_15_CODE,
        'format': 'FormatOne',
        'state': 'import',
        'progress_indicator': 0,
        # 'address_id': 3,
        # 'stock_journal_id': 20,
        # 'location_id': 12,
        # 'location_dest_id': 13,
    }

    def onchange_stock_journal_id(self, cr, uid, ids, stock_journal_id, context=None):
            context = context or self.pool['res.users'].context_get(cr, uid)
            vals = {}
            if stock_journal_id:
                stock_journal = self.pool['stock.journal'].browse(cr, uid, stock_journal_id, context)
                address_id = stock_journal.warehouse_id and stock_journal.warehouse_id.partner_address_id and stock_journal.warehouse_id.partner_address_id.id
                if address_id:
                    vals.update({'address_id': address_id})
                location_id = stock_journal.lot_input_id and stock_journal.lot_input_id.id
                if location_id:
                    vals.update({'location_id': location_id})
                location_dest_id = stock_journal.lot_output_id and stock_journal.lot_output_id.id
                if location_dest_id:
                    vals.update({'location_dest_id': location_dest_id})
            return {'value': vals}


class pricelist_import(filedata_import):
    _name = "pricelist.import"
    _description = "Import pricelist from file ."

    importer = pricelist_importer

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Supplier', required=False, domain="[('supplier', '=', True)]"),
        'pricelist_id': fields.many2one(
            'product.pricelist', 'Pricelist'
        ),
        'pricelist_version_id': fields.many2one(
            'product.pricelist.version',
            'Pricelist Version',
            domain="[('pricelist_id', '=', pricelist_id)]"
        ),
        'state': fields.selection(
            (
                ('import', 'import'),
                ('preview', 'preview'),
                ('end', 'end')
            ), 'state', required=True, translate=False, readonly=True
        ),
        'format': fields.selection(
            (
                ('FormatOne', _('Format One')),
                ('FormatTwo', _('Format Two')),
            ), 'Formato Dati', required=True, readonly=False
        ),
        'content_base64': fields.binary(
            'Pricelist file path', required=False, translate=False
        ),
        'file_name': fields.char('File Name', size=256),
        'content_text': fields.binary(
            'File Partner', required=False, translate=False
        ),
        'preview_text_original': fields.binary(
            'Preview text original', required=False,
            translate=False, readonly=True
        ),
        'preview_text_decoded': fields.text(
            'Preview text decoded', required=False,
            translate=False, readonly=True
        ),
        'progress_indicator': fields.integer(
            'Progress import ', size=3, translate=False, readonly=True
        ),
    }

    # default value for data fields of object
    _defaults = {
        'format': 'FormatOne',
        'state': 'import',
        'progress_indicator': 0,
    }


class sales_import(filedata_import):
    _name = "sales.import"
    _description = "Import Sale Order from file ."

    importer = sales_importer

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer', required=True, domain="[('customer', '=', True)]"),
        'date_order': fields.date('Date', required=True),
        'origin': fields.char('Origin', size=16),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True),
        'location_id': fields.many2one(
            'stock.location', 'Location',
            select=True,
            domain="[('usage', '!=', 'view')]"
        ),
        'auto_approve': fields.boolean('Auto Approve Sale Order and Picking',
            help="if set, the importer will also confirm Sale Order and Stock Picking. Also create Invoice"),
        'update_price': fields.boolean('Use price from file',
            help="if set, the importer will use the price from file and not from Listprice"),

        'state': fields.selection(
            (
                ('import', 'import'),
                ('preview', 'preview'),
                ('end', 'end')
            ), 'state', required=True, translate=False, readonly=True
        ),
        'format': fields.selection(
            (
                ('FormatOne', _('Format One')),
            ), 'Formato Dati', required=True, readonly=False
        ),
        'content_base64': fields.binary(
            'Sale file path', required=False, translate=False
        ),
        'file_name': fields.char('File Name', size=256),
        'content_text': fields.binary(
            'File Sale', required=False, translate=False
        ),
        'preview_text_original': fields.binary(
            'Preview text original', required=False,
            translate=False, readonly=True
        ),
        'preview_text_decoded': fields.text(
            'Preview text decoded', required=False,
            translate=False, readonly=True
        ),
        'progress_indicator': fields.integer(
            'Progress import ', size=3, translate=False, readonly=True
        ),
    }

    # default value for data fields of object
    _defaults = {
        'format': 'FormatOne',
        'state': 'import',
        'progress_indicator': 0,
    }


class invoice_import(filedata_import):
    _name = "invoice.import"
    _description = "Import Invoice from file ."

    importer = invoice_importer

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer', domain="[('customer', '=', True)]"),
        'date_invoice': fields.date('Date'),
        'origin': fields.char('Origin', size=16),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'account_id': fields.many2one('account.account', 'Account', domain=[('type', '!=', 'view'), ('type', '!=', 'closed')]),
        'type': fields.selection([
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Supplier Invoice'),
            ('out_refund', 'Customer Refund'),
            ('in_refund', 'Supplier Refund'),
            ], 'Type', required=True),
        'location_id': fields.many2one(
            'stock.location', 'Location',
            select=True,
            domain="[('usage', '!=', 'view')]"
        ),
        'auto_approve': fields.boolean('Auto Approve',
            help="if set, the importer will also confirm Invoice"),
        'update_price': fields.boolean('Use price from file',
            help="if set, the importer will use the price from file and not from Listprice"),
        'state': fields.selection(
            (
                ('import', 'import'),
                ('preview', 'preview'),
                ('end', 'end')
            ), 'state', required=True, translate=False, readonly=True
        ),
        'format': fields.selection(
            (
                ('FormatOne', _('Format One')),
                ('FormatTwo', _('Format Two')),
                ('FormatThree', _('Format Three')),
            ), 'Formato Dati', required=True, readonly=False
        ),
        'content_base64': fields.binary(
            'Invoice file path', required=False, translate=False
        ),
        'file_name': fields.char('File Name', size=256),
        'content_text': fields.binary(
            'File Partner', required=False, translate=False
        ),
        'preview_text_original': fields.binary(
            'Preview text original', required=False,
            translate=False, readonly=True
        ),
        'preview_text_decoded': fields.text(
            'Preview text decoded', required=False,
            translate=False, readonly=True
        ),
        'progress_indicator': fields.integer(
            'Progress import ', size=3, translate=False, readonly=True
        ),
    }

    # default value for data fields of object
    _defaults = {
        'format': 'FormatOne',
        'state': 'import',
        'progress_indicator': 0,
    }

    def on_change_type(self, cr, uid, ids, type, context):
        result = {}
        warning = {}
        matrix = {
            'out_invoice': 'sale',
            'in_invoice': 'purchase',
            'out_refund': 'sale_refund',
            'in_refund': 'purchase_refund',
        }

        domain = {
            'journal_id': [('type', '=', matrix.get(type))]
        }

        return {'value': result, 'domain': domain, 'warning': warning}


class inventory_import(filedata_import):
    _name = "inventory.import"
    _description = "Import Inventory from file ."

    importer = inventory_importer

    _columns = {
        'location_id': fields.many2one('stock.location', 'Location', domain="[('usage','!=','view')]", required=True),
        'date': fields.datetime("Date of inventory", help="Using 'Fill inventory' wizard, the inventory will be calculated at this date", required=True),
        'state': fields.selection(
            (
                ('import', 'import'),
                ('preview', 'preview'),
                ('end', 'end')
            ), 'state', required=True, translate=False, readonly=True
        ),
        'format': fields.selection(
            (
                ('FormatOne', _('Format One')),
                ('FormatTwo', _('Format Two')),
                ('FormatThree', _('Format Three')),
            ), 'Formato Dati', required=True, readonly=False
        ),
        'content_base64': fields.binary(
            'Inventory file path', required=False, translate=False
        ),
        'file_name': fields.char('File Name', size=256),
        'content_text': fields.binary(
            'File Partner', required=False, translate=False
        ),
        'preview_text_original': fields.binary(
            'Preview text original', required=False,
            translate=False, readonly=True
        ),
        'preview_text_decoded': fields.text(
            'Preview text decoded', required=False,
            translate=False, readonly=True
        ),
        'progress_indicator': fields.integer(
            'Progress import ', size=3, translate=False, readonly=True
        ),
    }

    # default value for data fields of object
    _defaults = {
        'format': 'FormatOne',
        'state': 'import',
        'progress_indicator': 0,
    }


class crm_import(filedata_import):
    _name = "crm.import"
    _description = "Import CRM Lead from file in .csv format."

    importer = crm_importer

    # data fields on DB table
    _columns = {
        # State of this wizard
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True),
        'state': fields.selection(
            (
                ('import', 'import'),
                ('preview', 'preview'),
                ('end', 'end')
            ), 'state', required=True, translate=False, readonly=True
        ),
        'format': fields.selection(
            (
                ('FormatOne', _('Format One')),
                ('FormatTwo', _('Format Two')),

            ), 'Formato Dati', required=True, readonly=False
        ),
        # Data of file, in code BASE64
        'content_base64': fields.binary(
            'CRM file path', required=False, translate=False
        ),
        'file_name': fields.char('File Name', size=256),
        # Data of file, in code text
        'content_text': fields.binary(
            'File Partner', required=False, translate=False
        ),
        # Codecs
        # 'text_encoding': fields.selection(
        #     [
        #         (ASCII_CODE, 'ascii'),
        #         (ISO_8859_15_CODE, 'iso-8859-15'),
        #         ('utf-8',  'Unicode 8')
        #     ], 'Text encoding', required=True, translate=False
        # ),
        # problem's row of product. original code
        'preview_text_original': fields.binary(
            'Preview text original', required=False,
            translate=False, readonly=True
        ),
        # problem's row of product. decoded
        'preview_text_decoded': fields.text(
            'Preview text decoded', required=False,
            translate=False, readonly=True
        ),

        'progress_indicator': fields.integer(
            'Progress import ', size=3, translate=False, readonly=True
        ),

    }
    # default value for data fields of object
    _defaults = {
        # 'text_encoding': ISO_8859_15_CODE,
        'state': 'import',
        'progress_indicator': 0,
    }


class bom_import(filedata_import):
    _name = "bom.import"
    _description = "Import bom from file in .xls format."

    importer = bom_importer

    # data fields on DB table
    _columns = {
        # State of this wizard
        'state': fields.selection(
            (
                ('import', 'import'),
                ('preview', 'preview'),
                ('end', 'end')
            ), 'state', required=True, translate=False, readonly=True
        ),
        'format': fields.selection(
            (
                ('FormatOne', _('Format One')),
                ('FormatTwo', _('Format Two')),
                ('FormatOmnitron', _('Format Omnitron'))
            ), 'Formato Dati', required=True, readonly=False
        ),
        # Data of file, in code BASE64
        'content_base64': fields.binary(
            'BOM file path', required=False, translate=False
        ),
        'file_name': fields.char('File Name', size=256),
        # Data of file, in code text
        'content_text': fields.binary(
            'File Partner', required=False, translate=False
        ),
        # Codecs
        # 'text_encoding': fields.selection(
        #     [
        #         (ASCII_CODE, 'ascii'),
        #         (ISO_8859_15_CODE, 'iso-8859-15'),
        #         ('utf-8',  'Unicode 8')
        #     ], 'Text encoding', required=True, translate=False
        # ),
        # problem's row of product. original code
        'preview_text_original': fields.binary(
            'Preview text original', required=False,
            translate=False, readonly=True
        ),
        # problem's row of product. decoded
        'preview_text_decoded': fields.text(
            'Preview text decoded', required=False,
            translate=False, readonly=True
        ),
        # Supplier
        # 'supplier': fields.many2one(
        #    'res.partner', 'Seller', required=True, translate=False
        # ),
        'progress_indicator': fields.integer(
            'Progress import ', size=3, translate=False, readonly=True
        ),
        # 'file_path': fields.char('Percorso file', size=256)
        'update_product_name': fields.boolean(
            'Update Product Name', help="If set, overwrite product name"
        )
    }
    # default value for data fields of object
    _defaults = {
        # 'text_encoding': ISO_8859_15_CODE,
        'state': 'import',
        'progress_indicator': 0,
    }
