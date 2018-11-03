# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author: Didotech SRL
#    Copyright 2015 Didotech SRL
#
#                       All Rights Reserved
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


class ir_model(orm.Model):
    _inherit = 'ir.model'
    def _get_ir_rule(self, cr, uid, ids, field_name, model_name, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        ir_rules_obj = self.pool['ir.rule']

        for model_id in ids:
            rule_ids = ir_rules_obj.search(cr, uid, [('model_id', '=', model_id)], context=context)
            result[model_id] = rule_ids
        return result

    _columns = {
        'ir_rules_ids': fields.function(_get_ir_rule, string='Record Rules', type='one2many', relation="ir.rule", readonly=True, method=True),
    }
