# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
from tools.translate import _
from openerp import SUPERUSER_ID


class res_partner(orm.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    _sql_constraints = [
        ('vat_uniq', 'unique (vat)', _('Error! Specified VAT Number already exists for any other registered partner.'))
    ]

    def vat_search(self, cr, ids, vat, context):
        # import pdb; pdb.set_trace()
        partner_vat = self.search(cr, SUPERUSER_ID, [('vat', '=', vat)], context=context)
        # partner_vat_dif = set(partner_vat).symmetric_difference(set(ids))
        if context.get('res_log_read', False):
            return True
        if partner_vat and ids not in partner_vat:
            partner = self.browse(cr, SUPERUSER_ID, partner_vat, context)[0]
            raise orm.except_orm(_('Error!'),
                _("Vat {vat} just exist on partner {partner} assigned to {user}!").format(vat=vat, partner=partner.name, user=partner.user_id.name or ''))
        partner_vat = self.search(cr, SUPERUSER_ID, [('vat', '=', vat), ('active', '=', False)], context=context)

        if partner_vat and ids not in partner_vat:
            partner = self.browse(cr, SUPERUSER_ID, partner_vat, context)[0]
            raise orm.except_orm(_('Error!'),
                _("Vat {vat} just exist non active partner {partner} assigned to {user}!").format(vat=vat, partner=partner.name, user=partner.user_id and partner.user_id.name or ''))
        return True

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if vals.get('vat', False):
            self.vat_search(cr, ids, vals.get('vat'), context)
        return super(res_partner, self).write(cr, uid, ids, vals, context)

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if vals.get('vat', False):
            self.vat_search(cr, [], vals.get('vat'), context)
        return super(res_partner, self).create(cr, uid, vals, context)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
