# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Andrea Cometa.
#    Email: info@andreacometa.it
#    Web site: http://www.andreacometa.it
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, orm


class res_partner(orm.Model):

    _name = "res.partner"
    _inherit = "res.partner"

    _columns = {
        'group_riba': fields.boolean("Group Ri.Ba.",
            help="Group Ri.Ba. by customer while issuing"),
        'not_use_vat_on_riba': fields.boolean("Non usare la P.IVA nella Ri.Ba.", help="Se selezionato nell'esportazione "),
        'company_riba_bank_id': fields.many2one('res.partner.bank', string='Company Ri.Ba bank for Bank Transfer', domain="[('company_id','=', company_id)]"),
    }

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if isinstance(ids, (int, long)):
            ids = [ids]

        if 'company_riba_bank_id' in vals:
            # search invoice
            invoice_obj = self.pool['account.invoice']
            invoice_ids = invoice_obj.search(cr, uid, [('partner_id', 'in', ids), ('type', '=', 'in_invoice'), ('state', '=', 'open'), ('bank_riba_id', '=', False)], context=context)
            if invoice_ids:
                bank_id = self.pool['res.partner.bank'].read(cr, uid, vals['company_riba_bank_id'], ['bank'], context, load='_obj')['bank']
                invoice_obj.write(cr, uid, invoice_ids, {'bank_riba_id': bank_id}, context)
        return super(res_partner, self).write(cr, uid, ids, vals, context)
