# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 didotech SRL (info at didotech.com)
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

from osv import fields
from osv import osv


class res_partner_zone(osv.osv):
    _name = 'res.partner.zone'
    _description = 'Zone of Commercial agents'

#    def make_name(self, cr, uid, context=None):
#        record = self.pool.get('ir.sequence').get(cr, uid, 'res.partner.zone')
#        default_name = '%s' %(record)
#        try:
#            return default_name
#        except Exception:
#            return default_name

    _columns = {
        'name': fields.char("Name", size=256, required=True),
        'province_ids': fields.many2many('res.province', 'res_province_partner_zone_rel', 'res_partner_zone_id', 'res_province_id', 'Provinces'),
    }
    _defaults = {
        #'name': make_name,
        'name': lambda self, cr, uid, context: self.pool.get('ir.sequence').get(cr, uid, 'res.partner.zone'),
    }
res_partner_zone()


class res_province(osv.osv):
    _inherit = 'res.province'
    _columns = {
        'res_partner_zone_ids': fields.many2many('res.partner.zone', 'res_province_partner_zone_rel', 'res_province_id', 'res_partner_zone_id', 'Zones'),
    }
res_province()


class res_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"
    _columns = {
        'res_partner_zone_id': fields.many2one('res.partner.zone', "zone's membership", ondelete='cascade'),
    }
res_partner()


class inherit_partner_zone(osv.osv):
    _inherit = 'res.partner.zone'
    _columns = {
        'res_partner_ids': fields.one2many('res.partner', "res_partner_zone_id", "zone's membership"),
    }
inherit_partner_zone()
