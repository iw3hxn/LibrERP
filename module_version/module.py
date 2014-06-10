# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Didotech srl (info at didotech.com)
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

from osv import fields, osv
from tools.translate import _


class module(osv.osv):
    _inherit = "ir.module.module"
    
    def _check_upgrade(self, cr, uid, ids, field_name=None, arg=None, context=None):
        installed_module_ids = self.search(cr, uid, [('state', 'in', ['installed', 'to upgrade', 'to remove'])])
        for module in self.browse(cr, uid, installed_module_ids):
            if not module.latest_version == self.get_module_info(module.name).get('version', '') and not module.need_upgrade:
                self.write(cr, uid, module.id, {'need_upgrade': True})
        
        res = {}
        for module_id in ids:
                res[module_id] = True
        return res
    
    def _need_upgrade(self, cr, uid, ids, field_name=None, arg=None, context=None):
        res = dict.fromkeys(ids, '')
        
        for module in self.browse(cr, uid, ids):
            if not module.latest_version == self.get_module_info(module.name).get('version', ''):
                res[module.id] = True
            else:
                res[module.id] = False
        return res
    
    _columns = {
        'need_upgrade': fields.function(_need_upgrade, string=_('Need Upgrade'), method=True, type='boolean', store=True),
        'check_upgrade': fields.function(_check_upgrade, string=_('Need Upgrade'), method=True, type='boolean', store=False)
    }
