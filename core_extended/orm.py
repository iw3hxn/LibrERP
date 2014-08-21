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

from openerp.osv import orm
from openerp.tools.config import config
import openerp.tools as tools
import logging
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
    for r in self.read(cr, user, ids, [self._rec_name], context, load='_classic_write'):
        if not self._rec_name in self._columns and not r.get(self._rec_name, False):
            _logger.error(u"Column '{column}' or function name_get() are not defined for table '{table}'".format(column=self._rec_name, table=self._name))
        
        if config['debug_mode']:
            result.append((r['id'], tools.ustr(r[self._rec_name])))
        else:
            result.append((r['id'], tools.ustr(r.get(self._rec_name, ''))))
    return result

orm.BaseModel.name_get = name_get
