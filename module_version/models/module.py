# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2015 Didotech srl (info at didotech.com)
#
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import logging

from openerp.osv import orm, fields
from tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class res_company(orm.Model):
    _inherit = "ir.module.module"
    
    def _check_upgrade(self, cr, uid, ids, field_name=None, arg=None, context=None):
        installed_module_ids = self.search(cr, uid, [('state', 'in', ['installed', 'to upgrade', 'to remove'])], context=context)
        update_module_ids = []
        for module in self.browse(cr, uid, installed_module_ids, context):
            if not module.latest_version == self.get_module_info(module.name).get('version', '') and not module.need_upgrade:
                update_module_ids.append(module.id)
        if update_module_ids:
            self.write(cr, uid, update_module_ids, {'need_upgrade': True}, context)
        
        res = {}
        for module_id in ids:
            res[module_id] = True
        return res
    
    def _need_upgrade(self, cr, uid, ids, field_name=None, arg=None, context=None):
        res = dict.fromkeys(ids, False)
        
        for module in self.browse(cr, uid, ids, context):
            if not module.latest_version == self.get_module_info(module.name).get('version', ''):
                res[module.id] = True
        return res
    
    _columns = {
        'need_upgrade': fields.function(_need_upgrade, string=_('Need Upgrade'), method=True, type='boolean', store=True),
        'check_upgrade': fields.function(_check_upgrade, string=_('Need Upgrade'), method=True, type='boolean', store=False)
    }

    def upgrade_modules(self, cr, uid, context=None, count=0):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if context.get('active_ids'):
            module_ids = context.get('active_ids')
        else:
            module_ids = self.search([('need_upgrade', '=', True), ('state', 'in', ('installed', 'to upgrade', 'to remove'))], context=context)

        self.button_upgrade(cr, uid, module_ids, context)

        modules_to_upgrade_ids = self.search(cr, uid, [('state', '=', 'to upgrade')], context=context)
        if modules_to_upgrade_ids:
            self.pool['base.module.upgrade'].upgrade_module(cr, uid, modules_to_upgrade_ids, context)

        modules_to_upgrade_ids = self.search(cr, uid, [('state', '=', 'to upgrade')], context=context)

        if count > 5:
            print 'Too many attempts'
            return False
        elif modules_to_upgrade_ids:
            count += 1
            _logger.info(u'Count: {count}'.format(count=count))
            context['active_ids'] = modules_to_upgrade_ids
            return self.upgrade_modules(cr, uid, context, count)
        else:
            return True
