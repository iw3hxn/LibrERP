# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012
#    Associazione OpenERP Italia (<http://www.openerp-italia.org>)
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
#############################################################################

from osv import fields, osv


class res_bank(osv.osv):
    _inherit = "res.bank"
    _columns = {
        'abi': fields.char('ABI', size=5),
        'cab': fields.char('CAB', size=5),
        'province': fields.many2one('res.province', string='Provincia', ondelete='restrict'),
    }

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=None):
        if not args:
            args = []
        context = context or self.pool['res.users'].context_get(cr, uid)
        if name:
            abi_cab = name.split(' ')
            if len(abi_cab) == 2 and abi_cab[0].isdigit() and abi_cab[1].isdigit():
                ids = self.search(cr, uid, [('abi', '=', abi_cab[0]), ('cab', '=', abi_cab[1])], limit=limit, context=context)
            else:
                ids = self.search(cr, uid, ['|', '|', ('abi', '=', name), ('cab', '=', name), ('name', 'like', name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for bank in self.browse(cr, uid, ids, context=context):
            if bank.abi and bank.cab:
                name = u"[{abi} {cab}] {name}".format(abi=bank.abi, cab=bank.cab, name=bank.name)
            else:
                name = bank.name
            res.append((bank.id, name))
        return res


class res_partner_bank(osv.osv):
    _inherit = "res.partner.bank"
    _columns = {
        'bank_abi': fields.char('ABI', size=5),
        'bank_cab': fields.char('CAB', size=5),
    }

    def onchange_bank_id(self, cr, uid, ids, bank_id, context=None):
        result = super(res_partner_bank, self).onchange_bank_id(cr, uid, ids, bank_id, context=context)
        if bank_id:
            bank = self.pool.get('res.bank').browse(cr, uid, bank_id, context=context)
            result['value']['bank_abi'] = bank.abi
            result['value']['bank_cab'] = bank.cab
        return result
