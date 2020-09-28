# -*- encoding: utf-8 -*-
# © 2020 Andrei Levin - Didotech srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm
import netsvc
wf_service = netsvc.LocalService("workflow")


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    def action_test_paid(self, cr, uid, context):
        if 'active_id' in context:
            invoice_id = context['active_id']
            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'act_paid', cr)

        return True
