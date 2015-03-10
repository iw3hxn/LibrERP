# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2015 Andrei Levin (andrei.levin at didotech.com)
#
#                          All Rights Reserved.
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
###############################################################################

from tools.translate import _
from datetime import datetime
import re
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class Utils():
    def updateProgressIndicator(self, cr, uid, ids):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        
        self.filedata_obj.write(cr, uid, ids, vals={'progress_indicator': self.progressIndicator}, context=self.context)
        _logger.info('Import status: %d %s (%d lines processed)' % (self.progressIndicator, '%', self.processed_lines))
        
    def toStr(self, value):
        number = re.compile(r'^[0-9.,]+$')
        number_vith_thousands_separator_italian = re.compile(r'[0-9]{1,3}(\.+[0-9]{3})+,[0-9]{2}$')
        number_vith_thousands_separator = re.compile(r'[0-9]{1,3}(,+[0-9]{3})+\.[0-9]{2}$')

        if isinstance(value, (str, unicode)):
            if number.match(value) and not value[0] == '0':
                if ',' in value or '.' in value:
                    if number_vith_thousands_separator_italian.match(value):
                        value = value.replace('.', '')
                    elif number_vith_thousands_separator.match(value):
                        value = value.replace(',', '')
                    value = value.replace(',', '.')
                    value = float(value)
                else:
                    value = int(value)
                return unicode(value)
            else:
                return value.strip()
        else:
            if value:
                return unicode(value)
            else:
                return False

    def simple_string(self, value):
        if isinstance(value, (str, unicode)):
            return value.strip()
        else:
            if value:
                return unicode(value)
            else:
                return False
    
    def notify_import_result(self, cr, uid, title, body='', error=False):
        EOL = '\n'

        if not error:
            body += EOL + EOL
            body += u"File '{0}' {1}{1}".format(self.file_name, EOL)
            body += _(u"Importate righe: {self.uo_new}{eol}Righe non importate: {self.problems}{eol}").format(self=self, eol=EOL)
            body += _(u"Righe aggiornate: {0}{1}").format(self.updated, EOL)
               
            if self.error:
                body += u'{0}{0}<strong>Errors:</strong>{0}'.format(EOL) + EOL.join(self.error)
                
            if self.warning:
                body += u'{0}{0}<strong>Warnings:</strong>{0}'.format(EOL) + EOL.join(self.warning)
        
        ## OpenERP v.6.1:
        self.pool.get('mail.message').create(cr, uid, {
            'subject': title,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'email_from': 'Data@Import',
            'user_id': uid,
            'body_text': body,
            'model': 'filedata.import'
        })
        
        ## OpenERP v.7:
        #self.pool.get('mail.message').create(cr, uid, {
        #    'subject': title,
        #    'author_id': uid,
        #    'type': 'notification',
        #    'body': body,
        #    'model': 'filedata.import'
        #})
        
        # Salva il messaggio nel database e chiudi la connessione
        cr.commit()
        cr.close()
