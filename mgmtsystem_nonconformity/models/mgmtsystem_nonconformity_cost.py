from tools.translate import _
import netsvc as netsvc
from openerp.osv import fields, orm


class mgmtsystem_nonconformity(orm.Model):
    """
    Management System - Nonconformity Costs
    """
    _name = 'mgmtsystem.nonconformity.cost'
    _description = 'Nonconformity Costs of the management system'

    _columns = {
        'name': fields.char('Name', required=True),
        'cost': fields.float('Cost', required=True),
        'mgmtsystem_nonconformity_id': fields.many2one('mgmtsystem.nonconformity', 'Nonconformity')
    }
