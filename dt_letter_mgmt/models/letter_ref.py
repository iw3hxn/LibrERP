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


class letter_ref(orm.Model):
    _name = 'letter.ref'

    def _name_get_intref(self, cr, uid, ids, prop, unknow_none, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.int_ref.name_get()[0]
            res.append((record.id, name[1]))
        return dict(res)

    def _links_get(self, cr, uid, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        obj = self.pool['res.request.link']
        ids = obj.search(cr, uid, [], context=context)
        res = obj.browse(cr, uid, ids, context)
        return [(r.object, r.name) for r in res]

    _columns = {
        'name': fields.char('Name', size=128, help="Subject of letter"),
        'int_ref': fields.reference('Reference', selection=_links_get, size=128),
        'ref_name': fields.function(_name_get_intref, method=True, type="char", string="Letter Reference"),
        'letter_id': fields.many2one('res.letter', "Letter"),
    }
    _defaults = {
        'name': lambda self, cr, uid, context: self.pool['ir.sequence'].get(cr, uid, 'letter.ref'),
    }

