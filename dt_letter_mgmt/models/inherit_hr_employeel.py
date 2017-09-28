# -*- encoding: utf-8 -*-
##############################################################################
#
#    Parthiv Pate, Tech Receptives, Open Source For Ideas
#    Copyright (C) 2009-Today Tech Receptives(http://techreceptives.com).
#    All Rights Reserved
#
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

import logging
import sys
import traceback

from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


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

DIRECTIONS = [
    ('in', 'IN'),
    ('out', 'OUT')
]


class hr_employee(orm.Model):
    _description = "Employee"
    _inherit = 'hr.employee'

    def _get_assigned_letters(self, cr, uid, ids, prop, unknow_none, context=None):
        if not len(ids):
            return {}
        model_name = super(hr_employee, self)._name
        res = []
        try:
            for id in ids:
                letter_ids = []
                ref_ids = self.pool['letter.ref'].search(cr, uid, [('int_ref', '=', model_name + ',' + str(id))],
                                                         context=context)
                if ref_ids:
                    for ref in self.pool['letter.ref'].read(cr, uid, ref_ids, context=context):
                        letter_ids.append(ref['letter_id'][0])
                res.append((id, letter_ids))
        except Exception, e:
            _logger.error(repr(traceback.extract_tb(sys.exc_traceback)))

        return dict(res)

    _columns = {
        'letter_ids': fields.function(_get_assigned_letters, method=True, string='Letter', type='one2many',
                                      relation="res.letter"),
    }

