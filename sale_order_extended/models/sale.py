# -*- coding: utf-8 -*-
# © 2018 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    @staticmethod
    def set_sequence(lines):
        sequence = 10
        for line in lines:
            if line[0] == 0:
                if line[2]['sequence'] == 10:
                    line[2]['sequence'] = sequence
                    sequence += 10
                elif line[2]['sequence'] > sequence:
                    next_sequence = line[2]['sequence'] / 10 * 10 + 10
                    if line[2]['sequence'] / 10 * 10 == line[2]['sequence']:
                        line[2]['sequence'] = sequence
                    sequence = next_sequence
            elif line[0] == 4:
                sequence += 10

        return lines

    def create(self, cr, uid, values, context=None):
        if 'order_line' in values:
            values['order_line'] = self.set_sequence(values['order_line'])
        return super(SaleOrder, self).create(cr, uid, values, context)

    def write(self, cr, uid, ids, values, context=None):
        if 'order_line' in values:
            values['order_line'] = self.set_sequence(values['order_line'])
        return super(SaleOrder, self).write(cr, uid, ids, values, context)
