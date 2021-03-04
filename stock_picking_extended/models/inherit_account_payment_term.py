from openerp.osv import orm


class AccountPaymentTerm(orm.Model):
    _inherit = 'account.payment.term'

    def name_get(self, cr, uid, ids, context=None):
        result = []
        for payment in self.browse(cr, uid, ids, context):
            name = payment.name
            if not payment.active:
                name = '!! NU !! ' + name
            result.append((payment.id, name))
        return result
