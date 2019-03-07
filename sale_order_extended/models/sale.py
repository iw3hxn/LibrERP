# -*- coding: utf-8 -*-
# © 2018-2019 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    @staticmethod
    def init_sequence(lines):
        for count, line in enumerate(lines, start=1):
            line[2]['sequence'] = count * 10
        return lines

    def create(self, cr, uid, values, context=None):
        if 'order_line' in values:
            values['order_line'] = self.init_sequence(values['order_line'])
        return super(SaleOrder, self).create(cr, uid, values, context)

    def set_sequence(self, cr, uid, lines):
        order_line_model = self.pool['sale.order.line']
        for count, line in enumerate(lines, start=1):
            if line[0] == 0:
                # Create
                if not 'sequence' in line[2]:
                    line[2]['sequence'] = count * 10
            elif line[0] == 1:
                # Update
                order_line = order_line_model.read(cr, uid, line[1], ('name', 'sequence'))
                if not 'sequence' in line[2]:
                    line[2]['sequence'] = order_line['sequence']
            elif line[0] == 2:
                # Delete
                order_line = order_line_model.read(cr, uid, line[1], ('name', 'sequence'))
                line[2] = {'sequence': order_line['sequence']}
            elif line[0] == 4:
                # Link
                order_line = order_line_model.read(cr, uid, line[1], ('name', 'sequence'))
                line[0] = 1
                line[2] = {'sequence': order_line['sequence']}

        lines = sorted(lines, key=lambda line: line[2]['sequence'])

        for count, line in enumerate(lines, start=1):
            line[2]['sequence'] = count * 10

        return lines

    def write(self, cr, uid, ids, values, context=None):
        if 'order_line' in values:
            values['order_line'] = self.set_sequence(cr, uid, values['order_line'])
        return super(SaleOrder, self).write(cr, uid, ids, values, context)


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(SaleOrderLine, self).default_get(cr, uid, fields, context)

        if 'order_id' in context and context['order_id']:
            order = self.pool['sale.order'].browse(cr, uid, context['order_id'], context)

            res['sequence'] = (len(order.order_line) + 1) * 10

        return res
