# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class ResUsers(orm.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    def __init__(self, cr, uid):
        super(ResUsers, self).__init__(cr, uid)
        self.cache_has_group = {}

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res_users_ids = super(ResUsers, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
        group_in = context.get('group_in', False)
        group_obj = self.pool['res.groups']
        if group_in:
            for res_user_id in res_users_ids:
                if not group_obj.user_in_group(cr, uid, res_user_id, group_in, context=context):
                    res_users_ids.remove(res_user_id)
        return res_users_ids

    def write(self, cr, uid, ids, vals, context=None):
        res = super(ResUsers, self).write(cr, uid, ids, vals, context)
        self.cache_has_group = {}
        res_groups = self.pool['res.groups']
        res_groups.cache_id_from_xml_id = {}
        res_groups.cache_user_in_group = {}
        return res

    def has_group(self, cr, uid, group_ext_id, context=None):
        """Checks whether user belongs to given group.
        :param cr
        :param uid
        :param str group_ext_id: external ID (XML ID) of the group.
           Must be provided in fully-qualified form (``module.ext_id``), as there
           is no implicit module to use..
        :param context
        :return: True if the current user is a member of the group with the
           given external ID (XML ID), else False.
        """
        assert group_ext_id and '.' in group_ext_id, "External ID must be fully qualified"
        cache_key = '{0}_{1}'.format(uid, group_ext_id).replace('.', '_')
        if self.cache_has_group.get(cache_key, False):
            return self.cache_has_group[cache_key]

        module, ext_id = group_ext_id.split('.')
        cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid IN
                        (SELECT res_id FROM ir_model_data WHERE module=%s AND name=%s)""",
                   (uid, module, ext_id))
        res = bool(cr.fetchone())
        self.cache_has_group[cache_key] = res
        return res
