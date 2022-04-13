from openerp.osv import orm, fields


class WizardRequirement(orm.TransientModel):
    _name = "wizard.requirement"
    _description = "Wizard Requirement"

    _columns = {
        'order_line_ids': fields.many2many('order.requirement.line', string='Lines', required=True),
    }

    def force(self, cr, uid, ids, context):
        wizard = self.browse(cr, uid, ids[0], context)
        order_requirement_line_model = self.pool['order.requirement.line']
        requirement_line_ids = []
        for line in wizard.order_line_ids:
            action_vals = line.action_open_bom()
            requirement_line_ids.append(action_vals['res_id'])

        # set to_buy
        for line in order_requirement_line_model.browse(cr, uid, requirement_line_ids, context):
            if not line.temp_mrp_bom_ids:
                line.write({'buy': True})

        return order_requirement_line_model.confirm_suppliers(cr, uid, requirement_line_ids, context)
