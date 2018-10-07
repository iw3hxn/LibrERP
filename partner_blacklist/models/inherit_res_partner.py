# -*- coding: utf-8 -*-

import time

import pooler
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID


COLOR_SELECTION = [
    ('aqua', (u"Aqua")),
    ('black', (u"Black")),
    ('blue', (u"Blue")),
    ('brown', (u"Brown")),
    ('cadetblue', (u"Cadet Blue")),
    ('darkblue', (u"Dark Blue")),
    ('fuchsia', (u"Fuchsia")),
    ('forestgreen', (u"Forest Green")),
    ('green', (u"Green")),
    ('grey', (u"Grey")),
    ('red', (u"Red")),
    ('orange', (u"Orange"))
]


class res_partner(orm.Model):
    _inherit = "res.partner"

    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        move_line_obj = self.pool['account.move.line']
        group_obj = self.pool['res.groups']
        fields_to_read = ['blacklist']
        partner_show_multicolor = group_obj.user_in_group(cr, uid, uid, 'partner_blacklist.partner_show_multicolor', context=context)
        if partner_show_multicolor:
            fields_to_read.append('payment_ids')

        for partner in self.read(cr, uid, ids, fields_to_read, context):
            if partner['blacklist']:
                value[partner['id']] = 'red'
            else:
                value[partner['id']] = 'black'
                if partner_show_multicolor:
                    payment_ids = partner['payment_ids']
                    if payment_ids:
                        if move_line_obj.search(cr, uid, [('id', 'in', payment_ids), ('date_maturity', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))], context=context):
                            value[partner['id']] = 'red'
                        else:
                            value[partner['id']] = 'orange'
        return value

    def onchange_blacklist(self, cr, uid, ids, blacklist, context=None):
        res = {}
        if blacklist:
            res['sale_warn'] = 'warning'
        return {'value': res}

    _columns = {
        'blacklist': fields.boolean('Blocked Partner', help="Remember to set advise on warning section"),
        'row_color': fields.function(get_color, string='Row color', type='char', readonly=True, method=True)
    }

