# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import re
from openerp.osv import orm, fields


# main mako-like expression pattern
EXPRESSION_PATTERN = re.compile('(\$\{.+?\})')


class mail_compose_message(orm.TransientModel):

    _inherit = 'mail.compose.message'

    def default_get(self, cr, uid, fields, context=None):

        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        result = super(mail_compose_message, self).default_get(cr, uid, fields, context=context)

        # link to model and record if not done yet
        if not result.get('model') or not result.get('res_id'):
            active_model = context.get('active_model')
            res_id = context.get('active_id')
            if active_model and active_model not in (self._name, 'mail.message'):
                result['model'] = active_model
                if res_id:
                    result['res_id'] = res_id
        else:
            active_model = result.get('model')
            res_id = result.get('res_id')

        # Try to provide default email_from if not specified yet
        if not result.get('email_from'):
            current_user = self.pool['res.users'].browse(cr, uid, uid, context)
            result['email_from'] = current_user.user_email or False
        if active_model in ['sale.order', 'crm.lead'] and not result.get('email_to'):
            result['email_to'] = self.pool[active_model].browse(cr, uid, res_id, context).contact_id.email

        return result

