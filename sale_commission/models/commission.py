# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp.osv import orm, fields
from tools.translate import _


class Commission(orm.Model):
    """Objeto comisión"""

    _name = "commission"
    _description = "Commission"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'type': fields.selection((('fix', 'Fix percentage'), ('sections', 'By sections')), 'Type', required=True),
        'fix_qty': fields.float('Fix Percentage'),
        'sections': fields.one2many('commission.section', 'commission_id', 'Sections'),
        'product_agent_ids': fields.one2many('product.agent.commission', 'commission_id', 'Agents'),
        'commission_ids': fields.one2many('hr.agent.commission', 'commission_id', 'Agents'),
    }
    _defaults = {
        'type': lambda *a: 'fix',
    }

    def calculate_sections(self, cr, uid, ids, base, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        commission = self.browse(cr, uid, ids, context)[0]
        for section in commission.sections:
            if abs(base) >= section.commission_from and (
                            abs(base) < section.commission_until or section.commission_until == 0):
                res = base * section.percent / 100.0
                return res
        return 0.0

    def get_commission(self, cr, uid, commission_ids, customer_id=None, context=None):
        if len(commission_ids) == 1:
            commission = self.browse(cr, uid, commission_ids[0], context)
            if commission.type == 'fix':
                if customer_id:
                    customers = {
                        agent_commission.customer_id.id: agent_commission.commission_percent
                        for agent_commission in commission.commission_ids
                    }
                    return customers.get(customer_id, commission.fix_qty)
                else:
                    return commission.fix_qty
            else:
                raise orm.except_orm(_('Error'), _('Commission by section is not yet implemented'))
        else:
            raise orm.except_orm(_('Error'), _('get_commission() takes exactly one commission_id'))
