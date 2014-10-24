# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

import datetime
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class wizard_download_attachments(orm.TransientModel):
    _name = "wizard.download.attachments"
    _description = 'Download products attachments'

    _columns = {
        'data': fields.binary("File", readonly=True),
        'name': fields.char('Filename', 32, readonly=True),
        'state': fields.selection((
            ('choose', 'choose'),   # choose
            ('get', 'get'),         # get the file
        )),
    }

    _defaults = {
        'state': lambda *a: 'choose',
    }

    def download_attachment(self, cr, uid, ids, context={}):
        attachment_obj = self.pool['ir.attachment']
        bom_obj = self.pool['mrp.bom']
        
        name = context.get('name', 'SO')
        file_name = '{0}_{1}.zip'.format(name, datetime.datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT))
        
        order_id = context.get('active_id', False)
        order = self.pool['sale.order'].browse(cr, uid, order_id, context)
        
        attachment_ids = set()
        for order_line in order.order_line:
            attachment_ids = attachment_ids.union(attachment_obj.search(cr, uid, [('res_model', '=', 'product.product'),
                                                                                  ('res_id', '=', order_line.product_id.id),
                                                                                  
                                                                                  ], context=context))
            
            if order_line.product_id.is_kit:
                main_bom_ids = bom_obj.search(cr, uid, [('product_id', '=', order_line.product_id.id), ('bom_id', '=', False)])
                if main_bom_ids:
                    if len(main_bom_ids) > 1:
                        _logger.warning(_(u"More than one BoM defined for the '{0}' product!").format(order_line.product_id.name))
                    
                    bom_ids = bom_obj.search(cr, uid, [('bom_id', '=', main_bom_ids[0])])
                    bom_product_ids = [bom.product_id.id for bom in bom_obj.browse(cr, uid, bom_ids)]
                    attachment_ids = attachment_ids.union(attachment_obj.search(cr, uid, [('res_model', '=', 'product.product'),
                                                                                          ('res_id', 'in', bom_product_ids),
                                                                                          ('active', '=', True)
                                                                                          ]))

        out = attachment_obj.get_as_zip(cr, uid, attachment_ids, log=True)
        return self.write(cr, uid, ids, {'state': 'get', 'data': out, 'name': file_name}, context=context)
