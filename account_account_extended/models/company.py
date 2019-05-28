# -*- encoding: utf-8 -*-
##############################################################################

from openerp.osv import orm, fields


class res_company(orm.Model):

    _inherit = 'res.company'

    def reload_chartofaccount_tree(self, cr, uid, ids, context=None):
        module_obj = self.pool['ir.module.module']

        cr.execute("ALTER TABLE account_account DROP parent_right")
        cr.execute("ALTER TABLE account_account DROP parent_left")
        cr.commit()

        module_ids = module_obj.search(cr, uid, [('name', '=', 'account_account_extended'), ('state', 'in', ('installed', 'to upgrade', 'to remove'))], context=context)

        module_obj.button_upgrade(cr, uid, module_ids, context)

        modules_to_upgrade_ids = module_obj.search(cr, uid, [('state', '=', 'to upgrade')], context=context)
        if modules_to_upgrade_ids:
            self.pool['base.module.upgrade'].upgrade_module(cr, uid, modules_to_upgrade_ids, context)

        return True
