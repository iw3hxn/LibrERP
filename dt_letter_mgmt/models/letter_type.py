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

from openerp.osv import orm, fields
from tools.translate import _

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


class letter_type(orm.Model):
    """Class to define various types for letters like: envelope, parcel, etc."""

    _name = 'letter.type'
    _description = "types for letters like: envelope, parcel, etc."

    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        for use in self.browse(cr, uid, ids, context):
            if use.color:
                value[use.id] = use.color
            else:
                value[use.id] = 'black'
        return value

    _columns = {
        'name': fields.char('Type', size=32, required=True),
        'code': fields.char('Code', size=8, required=True),
        'active': fields.boolean('Active'),
        'move': fields.selection(DIRECTIONS, 'Move', help="Incoming or Outgoing Letter"),
        'color': fields.selection(COLOR_SELECTION, 'Color'),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True),
        'model': fields.many2one('ir.model', 'Model', required=False),
    }

    _defaults = {
        'active': True,
    }

    _order = "code"
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code must be unique!'),
    ]

    def get_letter_type(self, cr, uid, model, context=None):
        type_id = self.search(cr, uid, [('model', '=', model)], context=context)
        if type_id:
            return type_id[0]
        else:
            raise orm.except_orm('Warning', _('Please create letter type for model {0}').format(model, ))
