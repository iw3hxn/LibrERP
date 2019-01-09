# -*- coding: utf-8 -*-
# © 2019 - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class WizardInventoryCosts(orm.TransientModel):
    _name = 'wizard.inventory.costs'

    _columns = {
        'file_name': fields.char('Nome File', size=256),
        'data': fields.binary('Excel', translate=False)
    }
