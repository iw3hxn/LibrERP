# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 Camptocamp Austria (<http://www.camptocamp.at>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, orm
from tools.translate import _
import time
import netsvc
import logging


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    #   def _get_state(self, cr, uid, ids, context=None):

    #       res = list(super(account_invoice, self)._columns['state'].selection)
    #       res.append(('draft_reset','Reset to draft'))

    #       return res

    #   _columns ={
    # FIXME the _get_state raises error
    #        'state': fields.selection(selection=_get_state, string='State', required=True),
    #       'state': fields.selection([
    #           ('draft','Draft'),
    #           ('draft_reset','Reset to Draft'),
    #           ('proforma','Pro-forma'),
    #           ('proforma2','Pro-forma'),
    #           ('open','Open'),
    #           ('paid','Paid'),
    #           ('cancel','Cancelled')
    #           ],'State', select=True, readonly=True,
    #           help=' * The \'Draft\' state is used when a user is encoding a new and unconfirmed Invoice. \
    #           \n* The \'Pro-forma\' when invoice is in Pro-forma state,invoice does not have an invoice number. \
    #           \n* The \'Open\' state is used when user create invoice,a invoice number is generated.Its in open state till user does not pay invoice. \
    #           \n* The \'Paid\' state is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled. \
    #           \n* The \'Cancelled\' state is used when user cancel invoice.'),

    #   }

    #    def _auto_init(self, cr, context=None):
    #           cr.execute("""update wkf_instance
    #                         set state = 'active'
    #                       where state = 'complete'
    #                         and res_type = 'account.invoice'
    #""")

    def action_reopen(self, cr, uid, ids, *args):
        _logger = logging.getLogger(__name__)
        context = self.pool['res.users'].context_get(cr, uid)
        attachment_obj = self.pool['ir.attachment']
        account_move_obj = self.pool['account.move']
        account_move_line_obj = self.pool['account.move.line']
        report_xml_obj = self.pool['ir.actions.report.xml']

        # _logger.debug('FGF reopen invoices %s' % (invoices))

        wf_service = netsvc.LocalService("workflow")

        move_ids = []  # ones that we will need to update
        now = ' ' + _('Invalid') + time.strftime(' [%Y%m%d %H%M%S]')
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.move_id:
                move_ids.append(invoice.move_id.id)
                _logger.debug('FGF reopen move_ids %s' % move_ids)
                for move in account_move_obj.browse(cr, uid, move_ids, context):
                    if not move.journal_id.reopen_posted:
                        raise orm.except_orm(_('Error !'), _(
                            'You can not reopen invoice of this journal [%s]! You need to need to set "Allow Update Posted Entries" first') % (
                                             move.journal_id.name))

            if invoice.payment_ids:
                pay_ids = account_move_line_obj.browse(cr, uid, invoice.payment_ids, context)
                for move_line in pay_ids:
                    if move_line.reconcile_id or (
                        move_line.reconcile_partial_id and move_line.reconcile_partial_id.line_partial_ids):
                        raise orm.except_orm(_('Error !'), _(
                            'You can not reopen an invoice which is partially paid! You need to unreconcile related payment entries first!'))
            self.write(cr, uid, invoice.id, {'state': 'draft'})
            wf_service.trg_delete(uid, 'account.invoice', invoice.id, cr)
            wf_service.trg_create(uid, 'account.invoice', invoice.id, cr)


        # # rename attachments (reports)
        # # for some reason datas_fname has .pdf.pdf extension
        # for inv in self.browse(cr, uid, ids):
        #     report_ids = report_xml_obj.search(cr, uid,
        #                                        [('model', '=', 'account.invoice'), ('attachment', '!=', False)])
        #     for report in report_xml_obj.browse(cr, uid, report_ids):
        #         if report.attachment:
        #             aname = report.attachment.replace('object', 'inv')
        #             if eval(aname):
        #                 aname = eval(aname) + '.pdf'
        #                 attachment_ids = attachment_obj.search(cr, uid, [('res_model', '=', 'account.invoice'),
        #                                                                  ('datas_fname', '=', aname),
        #                                                                  ('res_id', '=', inv.id)])
        #                 for a in attachment_obj.browse(cr, uid, attachment_ids):
        #                     vals = {
        #                         'name': a.name.replace('.pdf', now + '.pdf'),
        #                         'datas_fname': a.datas_fname.replace('.pdf.pdf', now + '.pdf.pdf')
        #                     }
        #                     attachment_obj.write(cr, uid, a.id, vals)

        # unset set the invoices move_id 
        self.write(cr, uid, ids, {'move_id': False}, context)

        if move_ids:

            for move in account_move_obj.browse(cr, uid, move_ids, context):
                name = move.name + now
                account_move_obj.write(cr, uid, [move.id], {'name': name})
                _logger.debug('FGF reopen move_copy moveid %s' % move.id)
                if move.journal_id.entry_posted:
                    raise orm.except_orm(_('Error !'),
                                         _('You can not reopen an invoice if the journal is set to skip draft!'))
                move_copy_id = account_move_obj.copy(cr, uid, move.id)
                _logger.debug('FGF reopen move_copy_id %s' % move_copy_id)
                name = name + '*'
                cr.execute("""update account_move_line
                                 set debit=credit, credit=debit, tax_amount= -tax_amount
                               where move_id = %s;""" % move_copy_id)
                account_move_obj.write(cr, uid, [move_copy_id], {'name': name}, context)
                _logger.debug('FGF reopen move_copy_id validate')
                account_move_obj.button_validate(cr, uid, [move_copy_id], context=context)
                _logger.debug('FGF reopen move_copy_id validated')
                # reconcile 
                r_id = self.pool.get('account.move.reconcile').create(cr, uid, {'type': 'auto'}, context)
                _logger.debug('FGF reopen reconcile_id %s' % r_id)
                line_ids = account_move_line_obj.search(cr, uid, [('move_id', 'in', [move_copy_id, move.id])], context=context)
                _logger.debug('FGF reopen reconcile_line_ids %s' % line_ids)
                lines_to_reconile = []
                for ltr in account_move_line_obj.browse(cr, uid, line_ids, context):
                    if ltr.account_id.id in (
                            ltr.partner_id.property_account_payable.id, ltr.partner_id.property_account_receivable.id):
                        lines_to_reconile.append(ltr.id)
                account_move_line_obj.write(cr, uid, lines_to_reconile, {'reconcile_id': r_id}, context)

        self._log_event(cr, uid, ids, -1.0, 'Reopened Invoice')

        return True

    #def action_move_create(self, cr, uid, ids, context=None):
    #    move_obj = self.pool.get('account.move')
    #    move_ids = [] # ones that we will need to update
    #    for inv in self.browse(cr, uid, ids, context=context):
    #        if inv.move_id:
    #            move_ids.append(inv.move_id.id)
    #        else:
    #            super(account_invoice, self).action_move_create(cr, uid, ids, context)
    #    if move_ids:
    #        move_obj.write(cr, uid, move_ids, {'state':'posted'})

    def action_number(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for inv in self.browse(cr, uid, ids, context=context):
            if not inv.internal_number:
                super(account_invoice, self).action_number(cr, uid, ids, context)
        return True
