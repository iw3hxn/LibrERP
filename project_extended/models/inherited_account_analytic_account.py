# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2016 Didotech Srl. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################.

from openerp.osv import orm

from tools.translate import _


class account_analytic_account(orm.Model):
    _inherit = 'account.analytic.account'

    _order = 'name asc'

    def _check_name_unique(self, cr, uid, ids, context=None):
        if len(ids) == 1:
            account = self.read(cr, uid, ids[0], ['name', 'parent_id'], context)
            name = account['name']
            parent_id = account['parent_id'] and account['parent_id'][0] or False
            account_ids = self.search(cr, uid, [('name', '=', name), ('parent_id', '=', parent_id)], context=context)
            if len(account_ids) > 1:
                return False
        return True

    _constraints = [
        (_check_name_unique, _("Name and Parent must be unique"), ['name', 'parent_id'])
    ]

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context.get('current_model') == 'project.project':
            del context['current_model']
        res = super(account_analytic_account, self).name_search(cr, uid, name, args, operator, context, limit)
        return res
