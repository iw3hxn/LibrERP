# -*- coding: utf-8 -*-
# © 2018-2020 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import netsvc
import tools
import os
import base64
import urllib2
from sys import platform
import logging

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from tools.translate import _

from report_aeroo_loffice.DocumentConverter import DocumentConversionException
from report_aeroo_loffice.report_loffice import OpenOffice_service
from report_aeroo.report_aeroo import aeroo_lock

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_url = 'http://www.alistek.com/aeroo_banner/v6_1_report_aeroo_ooo.png'


class AerooConfigInstaller(orm.TransientModel):
    _name = 'aeroo_config_lo.installer'
    _inherit = 'res.config.installer'
    # _rec_name = 'host'
    _logo_image = None

    def _get_image(self, cr, uid, context=None):
        if self._logo_image:
            return self._logo_image
        try:
            im = urllib2.urlopen(_url.encode("UTF-8"))
            if im.headers.maintype!='image':
                raise TypeError(im.headers.maintype)
        except Exception, e:
            path = os.path.join('report_aeroo', 'config_pixmaps', 'module_banner.png')
            image_file = file_data = tools.file_open(path, 'rb')
            try:
                file_data = image_file.read()
                self._logo_image = base64.encodestring(file_data)
                return self._logo_image
            finally:
                image_file.close()
        else:
            self._logo_image = base64.encodestring(im.read())
            return self._logo_image

    def _get_image_fn(self, cr, uid, ids, name, args, context=None):
        image = self._get_image(cr, uid, context)
        return dict.fromkeys(ids, image)  # ok to use .fromkeys() as the image is same for all

    _columns = {
        'soffice': fields.char('Path to LibreOffice executable', size=256, required=True),
        'dir_tmp': fields.char('Temp directory', size=256, required=True),
        'state': fields.selection([
            ('init', 'Init'),
            ('error', 'Error'),
            ('done', 'Done')
        ], 'State', select=True, readonly=True),
        'msg': fields.text('Message', readonly=True),
        'error_details': fields.text('Error Details', readonly=True),
        'config_logo': fields.function(_get_image_fn, string='Image', type='binary', method=True)
    }

    def default_get(self, cr, uid, fields, context=None):
        values = super(AerooConfigInstaller, self).default_get(cr, uid, fields, context=context)
        if platform == "linux" or platform == "linux2":
            # linux
            values['soffice'] = '/usr/bin/soffice'
        elif platform == "darwin":
            # OS X
            values['soffice'] = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
        elif platform == "win32":
            values['soffice'] = '/path/to/soffice'
        return values

    def check(self, cr, uid, ids, context=None):
        config_obj = self.pool['oo.config']
        data = self.read(cr, uid, ids, ['soffice', 'dir_tmp'])[0]
        del data['id']
        config_id = config_obj.search(cr, 1, [], context=context)
        if config_id:
            config_obj.write(cr, 1, config_id, data, context=context)
        else:
            config_id = config_obj.create(cr, 1, data, context=context)

        try:
            with tools.file_open('report_aeroo_loffice/test_temp.odt', mode='rb') as fp:
                file_data = fp.read()

            DC = netsvc.Service._services.setdefault(
                'openoffice',
                OpenOffice_service(cr, data['soffice'], data['dir_tmp'])
            )
            with aeroo_lock:
                DC.putDocument(file_data)
                pdf_data = DC.saveByStream(u'writer_pdf_Export')
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
            msg = _('Connection to LibreOffice.org instance was not established or convertion to PDF unsuccessful!')
        else:
            msg = _('Connection to the LibreOffice.org instance was successfully established and PDF convertion is working.')

        _logger.info(u'Info: {msg}'.format(msg=msg))
        _logger.info(u'New path is {path}'.format(path=data['soffice']))

        return self.write(cr, uid, ids, {'msg': msg, 'error_details': error_details, 'state': state})

    _defaults = {
        'config_logo': _get_image,
        'dir_tmp': '/tmp',
        'state': 'init',
    }
