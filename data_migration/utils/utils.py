# -*- coding: utf-8 -*-
# © 2013-2018 Andrei Levin - Didotech srl (www.didotech.com)

import logging
import re
from datetime import datetime

from tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class Utils():
    def updateProgressIndicator(self, cr, uid, ids):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        
        self.filedata_obj.write(cr, uid, ids, vals={'progress_indicator': self.progressIndicator}, context=self.context)
        _logger.info('Import status: %d %s (%d lines processed)' % (self.progressIndicator, '%', self.processed_lines))

    def update_progress_indicator(self, cr, uid, ids):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        self.filedata_obj.write(cr, uid, ids, vals={'progress_indicator': self.progress_indicator}, context=self.context)
        _logger.info('Import status: %d %s (%d lines processed)' % (self.progress_indicator, '%', self.processed_lines))

    @staticmethod
    def toStr(value):
        if isinstance(value, str):
            value = value.decode('UTF8')
        try:
            if value and not value == '\\N':
                if isinstance(value, (unicode, str)):
                    if value.lower() == 'null':
                        return False

                    number = re.compile(r'^(?!0[0-9])[0-9.,]+(?<![.,])$')
                    number_with_thousands_separator_italian = re.compile(r'[0-9]{1,3}(\.+[0-9]{3})+,[0-9]{2}$')
                    number_with_thousands_separator = re.compile(r'[0-9]{1,3}(,+[0-9]{3})+\.[0-9]{2}$')

                    value = value.strip(u'€ ')

                    if number.match(value):
                        if ',' in value or '.' in value:
                            if number_with_thousands_separator_italian.match(value):
                                value = value.replace('.', '')
                            elif number_with_thousands_separator.match(value):
                                value = value.replace(',', '')
                            else:
                                if value[0] == '+':
                                    return unicode(value)
                                elif value.count('.') > 1:
                                    # not a number
                                    return unicode(value)

                            value = value.replace(',', '.')

                            if value in ['.', ',']:
                                return 0

                            value = float(value)
                        else:
                            value = int(value)
                        return unicode(value)
                    else:
                        return value.strip()
                else:
                    if value:
                        if int(value) == value:
                            # Trim .0
                            return unicode(int(value))
                        else:
                            return unicode(value)
                    else:
                        return False
            else:
                return False
        except Exception as e:
            _logger.error(u'Error {error}'.format(error=e))
            return False

    def simple_string(self, value, as_integer=False):
        if isinstance(value, (str, unicode)):
            number = re.compile(r'^[0-9.,]+$')
            if as_integer and number.match(value):
                return unicode(int(float(value)))
            return value.strip()
        else:
            if value:
                return unicode(value)
            else:
                return False
    
    def notify_import_result(self, cr, uid, title, body='', error=False, record=False):
        EOL = '\n<br/>'
        end_time = datetime.now()
        duration_seconds = (end_time - self.start_time).seconds
        duration = '{min}m {sec}sec'.format(min=duration_seconds / 60, sec=duration_seconds - duration_seconds / 60 * 60)
        user = self.pool['res.users'].browse(cr, uid, uid, context=self.context)

        if not error:
            body += EOL + EOL
            body += u"File '{0}' {1}{1}".format(self.file_name, EOL)
            body += _(u"Importate righe: {self.uo_new}{eol}Righe non importate: {self.problems}{eol}").format(self=self, eol=EOL)
            body += _(u"Righe aggiornate: {0}{1}").format(self.updated, EOL)
            body += _('Inizio: {0}{1}').format(self.start_time.strftime('%Y-%m-%d %H:%M:%S'), EOL)
            body += _('Fine: {0}{1}').format(end_time.strftime('%Y-%m-%d %H:%M:%S'), EOL)
            body += _('Importazione eseguita in: {0}{1}{1}').format(duration, EOL)
            if self.error:
                body += u'{0}{0}<strong>Errors:</strong>{0}'.format(EOL) + EOL.join(self.error)
                
            if self.warning:
                body += u'{0}{0}<strong>Warnings:</strong>{0}'.format(EOL) + EOL.join(self.warning)
        
        # OpenERP v.6.1:
        mail_id = self.pool['mail.message'].create(cr, uid, {
            'subject': title,
            'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'email_from': user.company_id.email or 'Data@Import',
            'email_to': user.user_email or '',
            'user_id': uid,
            'body_text': body,
            'body_html': body,
            'model': 'filedata.import',
            'state': 'outgoing',
            'subtype': 'html',
        })

        if record:
            # add file to attachment of email for future use
            self.pool['mail.message'].write(cr, uid, mail_id, {
                'attachment_ids': [(0, 0, {
                    'res_model': 'mail.message',
                    'name': record.file_name.split('\\')[-1],
                    'datas_fname': record.file_name,
                    'datas': record.content_base64,
                    'res_id': mail_id
                })]
            })

        
        # OpenERP v.7:
        # self.pool.get('mail.message').create(cr, uid, {
        #    'subject': title,
        #    'author_id': uid,
        #    'type': 'notification',
        #    'body': body,
        #    'model': 'filedata.import'
        # })
        
        # Salva il messaggio nel database e chiudi la connessione
        cr.commit()
        cr.close()
