# -*- encoding: utf-8 -*-

from openerp.osv import orm
import time
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class IrFilters(orm.Model):
    _inherit = 'ir.filters'
    
    def global_filter(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'user_id': False}, context)

    def own_filter(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'user_id': uid}, context)
