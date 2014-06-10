# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 - TODAY DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2011 - TODAY Didotech Inc. (<http://www.didotech.com>)
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
##############################################################################
# Carlo use this url for help
# https://developers.google.com/google-apps/contacts/v1/developers_guide_python


from osv import fields,osv
from tools.translate import _

class google_contact_account_sync(osv.osv_memory):
    _name = 'google.contact_account.sync'
    _description = 'Google Contact Account syncronization'
    
    def sync(self, cr, uid, ids, context=None):
        value = {}
        account_id = context and context.get('active_id', False) or False
        if account_id:
            self.pool.get('google.contact_account').openerp_google_sync(cr, uid, account_id,context=context)
        return {'type':'ir.actions.act_window_close'}
google_contact_account_sync()