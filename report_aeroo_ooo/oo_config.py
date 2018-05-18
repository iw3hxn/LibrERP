##############################################################################
#
# Copyright (c) 2008-2011 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
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

from osv import osv, fields
import tools
import os, base64
import urllib2
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

_url = 'http://www.alistek.com/aeroo_banner/v6_1_report_aeroo_ooo.png'


class oo_config(osv.osv):
    '''
        OpenOffice connection
    '''
    _name = 'oo.config'
    _description = 'OpenOffice connection'

    _columns = {
        'host': fields.char('Host', size=128, required=True),
        'port': fields.integer('Port', required=True),
        'ooo_restart_cmd': fields.char('OOO restart command', size=256, \
                                       help='Enter the shell command that will be executed to restart the LibreOffice/OpenOffice background process. ' + \
                                            'The command will be executed as the user of the OpenERP server process,' + \
                                            'so you may need to prefix it with sudo and configure your sudoers file to have this command executed without password.'),

    }


class report_xml(osv.osv):
    _name = 'ir.actions.report.xml'
    _inherit = 'ir.actions.report.xml'

    _columns = {
        'process_sep': fields.boolean('Process Separately'),

    }


class aeroo_config_installer_master(osv.osv_memory):
    _name = 'aeroo_config.installer'
    _inherit = 'res.config.installer'
    _rec_name = 'host'
    _logo_image = None

    def _get_image(self, cr, uid, context=None):
        if self._logo_image:
            return self._logo_image
        try:
            im = urllib2.urlopen(_url.encode("UTF-8"))
            if im.headers.maintype != 'image':
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
        'host': fields.char('Host', size=64, required=True),
        'port': fields.integer('Port', required=True),
        'ooo_restart_cmd': fields.char('OOO restart command', size=256, \
                                       help='Enter the shell command that will be executed to restart the LibreOffice/OpenOffice background process.' + \
                                            'The command will be executed as the user of the OpenERP server process,' + \
                                            'so you may need to prefix it with sudo and configure your sudoers file to have this command executed without password.'),
        'state': fields.selection([
            ('init', 'Init'),
            ('error', 'Error'),
            ('done', 'Done'),

        ], 'State', select=True, readonly=True),
        'msg': fields.text('Message', readonly=True),
        'error_details': fields.text('Error Details', readonly=True),
        'link': fields.char('Installation Manual', size=128, help='Installation (Dependencies and Base system setup)',
                            readonly=True),
        'config_logo': fields.function(_get_image_fn, string='Image', type='binary', method=True),

    }

    def default_get(self, cr, uid, fields, context=None):
        config_obj = self.pool.get('oo.config')
        data = super(aeroo_config_installer_master, self).default_get(cr, uid, fields, context=context)
        ids = config_obj.search(cr, 1, [], context=context)
        if ids:
            res = config_obj.read(cr, 1, ids[0], context=context)
            del res['id']
            data.update(res)
        return data

    _defaults = {
        'config_logo': _get_image,
        'host': 'localhost',
        'port': 8100,
        'ooo_restart_cmd': 'sudo /etc/init.d/office_init  restart',
        'state': 'init',
        'link': 'http://www.alistek.com/wiki/index.php/Aeroo_Reports_Linux_server#Installation_.28Dependencies_and_Base_system_setup.29',
    }
