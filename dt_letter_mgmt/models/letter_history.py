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
import time

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


class letter_history(orm.Model):
    _name = "letter.history"
    _description = "Letter Communication History"
    _order = "id desc"

    _columns = {
        'register_id': fields.many2one('res.letter', 'Register'),
        'name': fields.char('Action', size=64),
        'date': fields.datetime('Date'),
        'user_id': fields.many2one('res.users', 'User Responsible', readonly=True),
    }

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
