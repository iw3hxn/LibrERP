# -*- encoding: utf-8 -*-
# © 2020 Andrei Levin - Didotech srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm


class Cron(orm.Model):
    _inherit = 'ir.cron'

    def action_disable_active(self, cr, uid, context=None):
        if context['active_ids']:
            self.write(cr, uid, context['active_ids'], {'active': False})
        return True
