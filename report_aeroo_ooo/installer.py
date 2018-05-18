# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2012 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
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

from osv import fields
from osv import osv
import netsvc
import tools
# from xml.dom import minidom
import os, base64
import urllib2

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from tools.translate import _

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
try:
    from report_aeroo_ooo.DocumentConverter import DocumentConversionException
    from report_aeroo_ooo.report import OpenOffice_service
except ImportError, e:
    _logger.error('Cannot `import {0}`'.format(e))  # Avoid init error if not installed

from report_aeroo.report_aeroo import aeroo_lock

_url = 'http://www.alistek.com/aeroo_banner/v6_1_report_aeroo_ooo.png'


class aeroo_config_installer(osv.osv_memory):
    _name = 'aeroo_config.installer'
    _inherit = 'aeroo_config.installer'

    def check(self, cr, uid, ids, context=None):
        config_obj = self.pool.get('oo.config')
        data = self.read(cr, uid, ids, ['host', 'port', 'ooo_restart_cmd'])[0]
        del data['id']
        config_id = config_obj.search(cr, 1, [], context=context)
        if config_id:
            config_obj.write(cr, 1, config_id, data, context=context)
        else:
            config_id = config_obj.create(cr, 1, data, context=context)

        try:
            fp = tools.file_open('report_aeroo_ooo/test_temp.odt', mode='rb')
            file_data = fp.read()
            DC = netsvc.Service._services.setdefault('openoffice', OpenOffice_service(cr, data['host'], data['port']))
            with aeroo_lock:
                DC.putDocument(file_data)
                DC.saveByStream()
                fp.close()
                DC.closeDocument()
                del DC
        except DocumentConversionException, e:
            netsvc.Service.remove('openoffice')
            error_details = str(e)
            state = 'error'
        except Exception, e:
            error_details = str(e)
            state = 'error'
        else:
            error_details = ''
            state = 'done'

        if state == 'error':
            msg = _('Connection to OpenOffice.org instance was not established or convertion to PDF unsuccessful!')
        else:
            msg = _(
                'Connection to the OpenOffice.org instance was successfully established and PDF convertion is working.')
        return self.write(cr, uid, ids, {'msg': msg, 'error_details': error_details, 'state': state}, context=context)

