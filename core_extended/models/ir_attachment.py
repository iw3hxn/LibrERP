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

import logging
import zipfile
from cStringIO import StringIO

from openerp.osv import orm

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class ir_attachment(orm.Model):
    _inherit = 'ir.attachment'
    
    def get_as_zip(self, cr, uid, ids, log=False, encode=True, compress=True):
        in_memory_zip = StringIO()

        context = self.pool['res.users'].context_get(cr, uid)

        if compress:
            zf = zipfile.ZipFile(in_memory_zip, "w", zipfile.ZIP_DEFLATED, False)
        else:
            zf = zipfile.ZipFile(in_memory_zip, "w", zipfile.ZIP_STORED, False)
        
        zf.debug = 3
        
        for attachment_id in ids:
            attachment = self.read(cr, uid, attachment_id, context=context)
            if attachment['name'] and attachment['datas']:
                # for the name can also be used attachment['datas_fname']
                zf.writestr(attachment['name'], attachment['datas'].decode("base64"))

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0
        
        if not zf.infolist():
            zf.writestr('empty', 'empty')
        
        if log:
            for info in zf.infolist():
                _logger.info(u"{0}, {1}, {2}, {3}".format(info.filename, info.date_time, info.file_size, info.compress_size))

        zf.close()
        
        in_memory_zip.seek(0)
        out = in_memory_zip.getvalue()
        
        if encode:
            return out.encode("base64")
        else:
            return out
