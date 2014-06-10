# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 - TODAY Denero Team. (<http://www.deneroteam.com>)
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
#
from osv import osv


class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'name' in vals:
            for address in self.pool.get('res.partner.address').browse(cr, uid, ids, context=context):
                if address.contact_id:
                    self.pool.get('res.partner.contact').write(cr, uid, [address.contact_id.id], {'last_name': vals['name']}, context=context)
                else:
                    contact_id = self.pool.get("res.partner.contact").create(cr, uid, {
                        'last_name': vals.get('name', address.complete_name),
                        'mobile': vals.get('mobile', address.mobile),
                        'title': vals.get('title', address.title and address.title.id or False),
                    }, context=context)
                    vals['contact_id'] = contact_id
        return super(res_partner_address, self).write(cr, uid, ids, vals, context)

    def create(self, cr, uid, data, context={}):
        if not data.get('contact_id', False):
            contact_id = self.pool.get("res.partner.contact").create(cr, uid, {
                'last_name': data.get('name', ''),
                'mobile': data.get('mobile', ''),
                'title': data.get('title', False),
            }, context=context)
            data['contact_id'] = contact_id
        return super(res_partner_address, self).create(cr, uid, data, context=context)
res_partner_address()
