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

import json
import logging
import zipfile
from cStringIO import StringIO

from requests import Session, Request

from openerp.osv import orm

_logger = logging.getLogger(__name__)


class IrAttachment(orm.Model):
    _inherit = 'ir.attachment'

    def get_as_zip(self, cr, uid, ids, log=False, encode=True, compress=True):
        _logger.info("get_as_zip: Starting function get_as_zip")
        _logger.debug("get_as_zip: Parameters - cr: %s, uid: %s, ids: %s, log: %s, encode: %s, compress: %s", cr, uid,
                      ids,
                      log, encode, compress)

        in_memory_zip = StringIO()

        context = self.pool['res.users'].context_get(cr, uid)

        if compress:
            zf = zipfile.ZipFile(in_memory_zip, "w", zipfile.ZIP_DEFLATED, False)
            _logger.debug("get_as_zip: ZIP_DEFLATED mode selected for compression")
        else:
            zf = zipfile.ZipFile(in_memory_zip, "w", zipfile.ZIP_STORED, False)
            _logger.debug("get_as_zip: ZIP_STORED mode selected for no compression")

        zf.debug = 3
        _logger.debug("get_as_zip: Debug level for zf set to 3")

        for attachment_id in ids:
            attachment = self.read(cr, uid, attachment_id, ['name', 'datas'], context)
            _logger.info("get_as_zip: Processing attachment ID: %s, name=%s", attachment_id, attachment['name'])
            if attachment['name'] and attachment['datas']:
                _logger.info("get_as_zip: Adding attachment to ZIP: %s", attachment['name'])
                # for the name can also be used attachment['datas_fname']
                zf.writestr(attachment['name'], attachment['datas'].decode("base64"))

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0
        _logger.debug("get_as_zip: Creation system for ZIP files set to 0")

        if not zf.infolist():
            _logger.warning("get_as_zip: Empty ZIP, adding 'empty' entry")
            zf.writestr('empty', 'empty')

        if log:
            _logger.info("get_as_zip: ZIP file details:")
            for info in zf.infolist():
                _logger.info("get_as_zip: %s, %s, %s, %s", info.filename, info.date_time, info.file_size,
                             info.compress_size)

        zf.close()

        in_memory_zip.seek(0)
        out = in_memory_zip.getvalue()
        _logger.debug("get_as_zip: Closing the ZIP file and gathering data")

        if encode:
            _logger.info("get_as_zip: Encoding output to base64")
            return out.encode("base64")
        else:
            return out

    def open_file(self, cr, uid, ids, context):
        if len(ids) > 1:
            return False
        # base_url = 'http://127.0.0.1:8069/web/binary/saveas'
        payload = {
            'token': u'1623250275576',
            'session_id': 'cf9a6989d49c48479c345343928c16d7',
            'data': json.dumps({
                "model": "ir.attachment",
                "id": ids[0],
                "field": "datas",
                "filename_field": "datas_fname",
                "context": context
            })
        }

        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url',
                                                                  default='http://localhost:8069', context=context) + '/web/binary/saveas_ajax'

        s = Session()
        p = Request('POST', base_url, params=payload).prepare()
        url = p.url
        return_vals = {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'current',
        }
        return return_vals
