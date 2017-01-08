# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import orm
from openerp.tools.translate import _


class AssetConfirmationWizard(orm.TransientModel):
    _name = "account.asset.confirm"

    def confirm(self, cr, uid, ids, context=None):
        ctx = dict(context or {})
        for asset in self.pool['account.asset.asset'].browse(
                cr, uid, context.get('active_ids', False), ctx):
            if asset.state == 'draft':
                asset.validate()
        return {
            'name': _('Confirmed Asset'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.asset.asset',
            'view_id': False,
            'domain': "[('id','in',[" + ','.join(
                map(str, context.get('active_ids', False))) + "])]",
            'type': 'ir.actions.act_window',
        }

    def set_to_draft(self, cr, uid, ids, context=None):
        ctx = dict(context or {})
        for asset in self.pool['account.asset.asset'].browse(
                cr, uid, context.get('active_ids', False), ctx):
            if asset.state == 'open':
                asset.set_to_draft()
        return {
            'name': _('Drafted Asset'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.asset.asset',
            'view_id': False,
            'domain': "[('id','in',[" + ','.join(
                map(str, context.get('active_ids', False))) + "])]",
            'type': 'ir.actions.act_window',
        }
