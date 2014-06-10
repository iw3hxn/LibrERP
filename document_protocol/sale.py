# -*- encoding: utf-8 -*-
################################################################################
#
# Copyright (c) 2013 Didotech.com (info at didotech.com)
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
################################################################################

from osv import fields, osv


class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'letter_id': fields.many2one('res.letter', 'Protocol', required=False),
    }
    
    def create(self, cr, uid, values, context=None):
        ## If letter_id is passed with values, it's a copy of existent sale.order.
        if not 'letter_id' in values:
            letter_type_id = self.pool.get('letter.type').get_letter_type(cr, uid, self._name, context)
            protocol_values = {
                'type': letter_type_id,
                'date': values['date_order'],
                'user_id': values['user_id'],
                'partner_id': values['partner_id'],
            }
            letter_type = self.pool.get('letter.type').browse(cr, uid, letter_type_id)
            values['letter_id'] = self.pool.get('res.letter').create(cr, uid, protocol_values, {'move': letter_type.move})
        return super(sale_order, self).create(cr, uid, values, context)
