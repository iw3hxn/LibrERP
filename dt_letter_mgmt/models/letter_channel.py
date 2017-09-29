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


class letter_channel(orm.Model):
    """ Class to define various channels using which letters can be sent or received like: post, fax, email. """

    _name = 'letter.channel'
    # Description can't be longer 64 chars
    _description = "channels using which letters can be sent/received like: post,fax"

    _columns = {
        'name': fields.char('Type', size=32, required=True),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
    }

    _order = "name"
