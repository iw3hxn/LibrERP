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


class ResGroups(orm.Model):
    _name = 'res.groups'
    _inherit = 'res.groups'

    def __init__(self, cr, uid):
        super(ResGroups, self).__init__(cr, uid)
        self.cache_id_from_xml_id = {}
        self.cache_user_in_group = {}

    def write(self, cr, uid, ids, vals, context=None):
        res = super(ResGroups, self).write(cr, uid, ids, vals, context)
        self.cache_id_from_xml_id = {}
        self.cache_user_in_group = {}
        res_users = self.pool['res.users']
        res_users.cache_has_group = {}

        return res

    def id_from_xml_id(self, cr, uid, xml_id, context=None):
        cache_key = '{0}_{1}'.format(uid, xml_id).replace('.', '_')
        if self.cache_id_from_xml_id.get(cache_key, False):
            return self.cache_id_from_xml_id[cache_key]
        context = context or self.pool['res.users'].context_get(cr, uid)
        group_obj = self.pool['res.groups']
        group_all_ids = group_obj.search(cr, uid, [], context=context)
        group_xml_ids = group_obj.get_xml_id(cr, uid, group_all_ids, context=context)
        
        for key in group_xml_ids.keys():
            xml_id_it = group_xml_ids[key]
            if xml_id_it == xml_id:
                self.cache_id_from_xml_id[cache_key] = key
                return key
        self.cache_id_from_xml_id[cache_key] = False
        return False

    def user_in_group(self, cr, uid, user_id, group_xml_id, context=None):
        cache_key = '{0}_{1}'.format(user_id, group_xml_id).replace('.', '_')
        if self.cache_user_in_group.get(cache_key, False):
            return self.cache_user_in_group[cache_key]
        context = context or self.pool['res.users'].context_get(cr, uid)
        user_obj = self.pool['res.users']
        user = user_obj.read(cr, uid, user_id, ['groups_id'], context=context)
        if isinstance(user, list):
            user = user[0]
        
        group_id = self.id_from_xml_id(cr, uid, group_xml_id, context=context)
        for group in user['groups_id']:
            if group == group_id:
                self.cache_user_in_group[cache_key] = True
                return True
        self.cache_user_in_group[cache_key] = False
        return False

