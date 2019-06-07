# -*- encoding: utf-8 -*-
##############################################################################

from openerp.osv import orm, fields


class account_account(orm.Model):
    _inherit = 'account.account'

    _order = "parent_left"
    _parent_order = "code"
    _parent_store = True

    _columns = {
        'code': fields.char('Code', size=64, required=True, select=1),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
    }


