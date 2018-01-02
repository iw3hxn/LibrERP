# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class MrpBom(orm.Model):
    _name = 'mrp.bom'
    _inherit = ['mail.thread', "mrp.bom"]

    def write(self, cr, uid, ids, values, context):
        if 'bom_lines' in values:
            for line in values['bom_lines']:
                if line[0] == 0:
                    message = _(u"Added Product: '{}', quantity: {}").format(
                        line[2]['name'], line[2]['product_qty'])
                    title = 'Added'
                elif line[0] == 1:
                    bom_line = self.browse(cr, uid, line[1], context)
                    updated = ["{}: {} -> {}".format(key, getattr(bom_line, key, ''), value) for key, value in line[2].items()]
                    message = _(u"Updated Product: '{}': {}").format(bom_line.product_id.default_code,
                                                                     ', '.join(updated))
                    title = 'Updated'
                elif line[0] == 2:
                    bom_line = self.browse(cr, uid, line[1], context)
                    message = _(u"Deleted Product: '{}'").format(bom_line.product_id.default_code)
                    title = 'Deleted'
                else:
                    message = False
                if message:
                    for bom_id in ids:
                        self.message_append(cr, uid, [bom_id], message, body_text=message, context=context)
                        # self.mail_post(cr, uid, bom_id, message, title, context)
        return super(MrpBom, self).write(cr, uid, ids, values, context)

    def mail_post(self, cr, uid, bom_id, body, title, context):
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        return self.pool['mail.message'].create(cr, uid, {
            'subject': title,
            'date': datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'email_from': user.company_id.email or 'BoM update',
            'email_to': '',
            'user_id': uid,
            'body_text': body,
            'body_html': body,
            'model': 'mrp.bom',
            'state': 'outgoing',
            'subtype': 'html',
            'res_id': bom_id
        })
