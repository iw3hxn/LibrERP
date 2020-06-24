# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Carlo Vettore (carlo.vettore at didotech.com)
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
from openerp.osv import orm, fields


class CrmPhonecall(orm.Model):
    _inherit = 'crm.phonecall'

    _defaults = {
        'partner_id': lambda self, cr, uid, context: context.get('partner_id', False),
    }


class CrmMeeting(orm.Model):
    _description = "Meeting"
    _inherit = 'crm.meeting'
    _columns = {
        # 'result': fields.selection([('+', '+'), ('-', '-'), ('=', '=')], 'Result'),
        'province_id': fields.related(
            'partner_address_id',
            'province',
            relation='res.province',
            type='many2one',
            string='Provincia',
            store=True,
            readonly=True),
    }

    _defaults = {
        'state': 'draft',
        'active': 1,
        'user_id': lambda self, cr, uid, ctx: uid,
        'partner_id': lambda self, cr, uid, context: context.get('partner_id', False),
        'partner_address_id': lambda self, cr, uid, context: context.get('partner_address_id', False),
        'email_from': lambda self, cr, uid, context: context.get('email_from', False),
        'categ_id': lambda self, cr, uid, context: context.get('categ_id', False)
    }

    _order = "date desc"
