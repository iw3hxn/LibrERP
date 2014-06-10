# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi. Copyright Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import platform
import os
import sys
from osv import fields, osv
import addons
import report_webkit

def get_lib(self, cursor, uid,):
    """Return absolute path of wkhtmlto pdf depending on OS and architecture"""
    res = {}
    curr_sys = platform.system()
    extention = u'i386'
    # As recomended in Python in order to support Mac os X
    if sys.maxsize > 2**32:
        extention = 'amd64'
    sysmapping = {'Linux': (u'linux', u'wkhtmltopdf-'+ extention),
                  'Darwin': (u'osx', u'wkhtmltopdf'),
                  'Windows': (u'windows', u'wkhtmltopdf.exe')}
    args = (u'report_webkit_lib', 'lib') + sysmapping[curr_sys]
    path = addons.get_module_resource(*args)
    print path
    if not os.access(path, os.X_OK):
        raise osv.except_osv(_('SystemError'),
                             _('%s is not executable' % (path)))
    return path
    
report_webkit.webkit_report.WebKitParser.get_lib = get_lib
