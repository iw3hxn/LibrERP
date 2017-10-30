# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class MrpBom(orm.Model):
    _inherit = "mrp.bom"

    _columns = {
        'deleted_bom_line_ids': fields.one2many(
            'mrp.bom', 'bom_id', string='Deleted BoMs', domain=[('active', '=', False)], readonly=True)
    }

    def write(self, cr, uid, ids, values, context):
        if 'bom_lines' in values:
            today = datetime.datetime.now()
            for line in values['bom_lines']:
                if line[0] == 0:
                    if 'date_start' not in line[2] or not line[2]['date_start']:
                        line[2]['date_start'] = today.strftime(DEFAULT_SERVER_DATE_FORMAT)
                elif line[0] == 2:
                    line[0] = 1
                    line[2] = {
                        'active': False,
                        'date_stop': today.strftime(DEFAULT_SERVER_DATE_FORMAT),
                    }
        return super(MrpBom, self).write(cr, uid, ids, values, context)
