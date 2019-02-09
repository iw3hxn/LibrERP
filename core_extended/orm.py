# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

import openerp.tools as tools
from openerp.osv import orm
from openerp.tools.config import config
from tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


# Monkey patching.
def name_get(self, cr, user, ids, context=None):
    """Returns the preferred display value (text representation) for the records with the
       given ``ids``. By default this will be the value of the ``name`` column, unless
       the model implements a custom behavior.
       Can sometimes be seen as the inverse function of :meth:`~.name_search`, but it is not
       guaranteed to be.

       :rtype: list(tuple)
       :return: list of pairs ``(id,text_repr)`` for all records with the given ``ids``.
    """
    if not ids:
        return []
    if isinstance(ids, (int, long)):
        ids = [ids]

    result = []
    # TODO Antonio Mignolli sol.1 test before apply!
    # When ids are in the form 'one2many_v_id_*' the following 'read' raise error (SQL: SELECT ... WHERE ID in ('one2many_v_')
    # for i in ids:
    #     if i and isinstance(i, str) and 'one2many' in i:
    #         raise orm.except_orm(_('Warning'), _('Save main element first'))
    #
    # TODO Antonio sol.2, version, don't popup but avoid SQL error, comment the read below and de-comment the rest
    # for r in self.read(cr, user, ids, [self._rec_name], context, load='_classic_write'):
    for i in ids:
        if i and isinstance(i, str) and 'one2many' in i:
            result.append((i, ''))
            continue
        r = self.read(cr, user, i, [self._rec_name], context, load='_classic_write')
        if self._rec_name not in self._columns and not r.get(self._rec_name, False):
            _logger.error(u"Column '{column}' or function name_get() are not defined for table '{table}'".format(column=self._rec_name, table=self._name))
        if r:
            if config['debug_mode']:
                result.append((r['id'], tools.ustr(r[self._rec_name])))
            else:
                result.append((r['id'], tools.ustr(r.get(self._rec_name, self._table))))
        else:
            result.append((i, ''))
    return result

orm.BaseModel.name_get = name_get
