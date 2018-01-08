# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class MrpBom(orm.Model):
    
    _inherit = "mrp.bom"

    def write(self, cr, uid, ids, values, context=None):
        if 'bom_lines' in values:
            for line in values['bom_lines']:
                if line[0] == 0:
                    message = _(u"Added Product: '{}', quantity: {}").format(
                        line[2]['name'], line[2]['product_qty'])
                    title = _('Added')
                elif line[0] == 1:
                    bom_line = self.browse(cr, uid, line[1], context)
                    updated = []
                    for key, value in line[2].items():
                        initial_value = getattr(bom_line, key) or ''
                        if initial_value and hasattr(initial_value, 'id'):
                            initial_value = initial_value.id

                        product_property = u"{}: {} -> {}".format(
                            key,
                            initial_value,
                            value
                        )
                        updated.append(product_property)

                    message = _(u"Updated Product: '{}': {}").format(bom_line.product_id.default_code,
                                                                     ', '.join(updated))
                    title = _('Updated')
                elif line[0] == 2:
                    bom_line = self.browse(cr, uid, line[1], context)
                    message = _(u"Deleted Product: '{}'").format(bom_line.product_id.default_code)
                    title = _('Deleted')
                else:
                    message = False
                if message:
                    for bom_id in ids:
                        self.revision_post(cr, uid, bom_id, title, message, context=context)
        return super(MrpBom, self).write(cr, uid, ids, values, context)

    def revision_post(self, cr, uid, bom_id, title, message, context):
        return self.pool['mrp.bom.revision'].create(cr, uid, {
            'name': title,
            'date': datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'author_id': uid,
            'description': message,
            'bom_id': bom_id
        }, context)
