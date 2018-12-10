# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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

# FIXME remove logger lines or change to debug

from openerp.osv import orm, fields
from openerp.tools.translate import _
import netsvc
import time
import logging


class stock_journal(orm.Model):
    _inherit = 'stock.journal'

    _columns = {
        'reopen_posted': fields.boolean('Allow Update of Posted Pickings',
                                        help="Allows to reopen posted pickings, as long no invoice is created or no other moves for the products of this picking are posted"),
    }

    _defaults = {
        'reopen_posted': True
    }


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    #    def _auto_init(self, cr, context=None):
    #           cr.execute("""update wkf_instance
    #                         set state = 'active'
    #                       where state = 'complete'
    #                         and res_type = 'stock.picking'
    # """)

    def allow_reopen(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)
        move_line_obj = self.pool['stock.move']
        account_invoice_obj = self.pool['account.invoice']
        _logger.debug('FGF picking allow open ids %s ' % ids)
        for picking in self.browse(cr, uid, ids, context):
            _logger.debug(
                'FGF picking allow open  %s %s' % (picking.stock_journal_id, picking.stock_journal_id.reopen_posted))
            if picking.stock_journal_id and not picking.stock_journal_id.reopen_posted:
                raise orm.except_orm(_('Error'), _(
                    'You cannot reset to draft pickings of this journal ! Please check "Allow Update of Posted Pickings" in Warehous Configuration / Stock Journals %s') % picking.stock_journal_id.name)
            if picking._columns.get('invoice_ids'):
                _logger.debug('FGF picking allow open inv_ids ')
                ids2 = []
                if picking.invoice_ids:
                    for inv in picking.invoice_ids:
                        if inv.state in ['cancel']:
                            pass
                        elif inv.state in ['draft']:
                            ids2.append(inv.id)
                        else:
                            raise orm.except_orm(_('Error'), _(
                                'You cannot reset a picking with an open invoice [%s] to draft ! You must reopen the invoice first (install modul account_invoice_reopen' % inv.number))
                    # account_invoice_obj.unlink(cr, uid, ids2)
                    # account_invoice_obj.write(cr, uid, ids2, {'state':'cancel'})
                    account_invoice_obj.action_cancel(cr, uid, ids2)
                    if ids2:
                        self.write(cr, uid, [picking.id], {'invoice_state': '2binvoiced'})
            elif picking.invoice_state == 'invoiced':
                _logger.debug('FGF picking invoiced ')
                raise orm.except_orm(_('Error'), _('You cannot reset an invoiced picking to draft !'))
            if picking.move_lines:
                for move in picking.move_lines:
                    # FIXME - not sure if date or id has to be checked or both if average price is used
                    # FGF 20121130 date_expected 
                    if move.product_id.cost_method == 'average' and picking.type == 'in':
                        later_ids = move_line_obj.search(cr, uid, [('product_id', '=', move.product_id.id),
                                                                   ('state', '=', 'done'),
                                                                   ('date_expected', '>', move.date),
                                                                   ('price_unit', '!=', move.price_unit),
                                                                   ('company_id', '=', move.company_id.id)], context=context)
                        if later_ids:
                            later_prices = []
                            for later_move in move_line_obj.browse(cr, uid, later_ids):
                                if later_move.purchase_line_id:
                                    later_prices.append(later_move.price_unit)
                                    raise orm.except_orm(_('Error'), _(
                                        'You cannot reopen this picking, because product "%s" of this picking has already later posted moves with different cost price(s) %s  then the current [%s] to be reopened! Recalculation of avarage price is not supported') % (
                                                     move.product_id.name, later_prices, move.price_unit))
        return True

    def action_reopen(self, cr, uid, ids, context=None):
        """ Changes picking and move state from done to confirmed.
        @return: True
        """
        _logger = logging.getLogger(__name__)
        self.allow_reopen(cr, uid, ids, context=context)
        move_line_obj = self.pool['stock.move']
        # account_move_line_obj = self.pool['account.move.line']
        account_move_obj = self.pool['account.move']
        account_invoice_obj = self.pool['account.invoice']
        report_xml_obj = self.pool['ir.actions.report.xml']
        attachment_obj = self.pool['ir.attachment']

        now = ' ' + _('Invalid') + time.strftime(' [%Y%m%d %H%M%S]')
        for pick in self.browse(cr, uid, ids, context):
            _logger.debug('FGF picking action reopen pick %s ' % (pick.name))
            ml_ids = []
            ml_real_time_ids = []
            for ml in pick.move_lines:
                ml_ids.append(ml.id)
                if ml.product_id.valuation == 'real_time':
                    ml_real_time_ids.append(ml.id)
            _logger.debug('FGF picking action reopen pick %s ' % (ml_ids))
            move_line_obj.write(cr, uid, ml_ids, {'state': 'draft'}, context)
            # we have to handle real time accounting stock moves
            if ml_real_time_ids:
                # FIXME - performance, should be an id - link to picking
                # aml_ids = account_move_line_obj.search(cr, uid, [('picking_id','=',pick.id)])
                move_all_ids = account_move_obj.search(cr, uid, [('ref', '=', pick.name)])
                # FIXME ugly hack
                # picking should reference move (as invoice)
                move_inv_ids = []
                move_ids = []
                invoice_ids = account_invoice_obj.search(cr, uid, [('move_id', 'in', move_all_ids)])
                for inv in account_invoice_obj.browse(cr, uid, invoice_ids, context):
                    move_inv_ids.append(inv.move_id)
                for m in move_all_ids:
                    if m not in move_inv_ids:
                        move_ids.append(m)
                # _logger.debug('FGF picking action reopen move_lines %s ' %(aml_ids)   )
                # move_ids = []
                # for aml in account_move_obj.browse(cr, uid, aml_ids):
                #    if aml.move_id.id not in move_ids:
                #        move_ids.append(aml.move_id.id)
                _logger.debug('FGF picking action reopen move %s ' % (move_ids))
                # account_move_obj.write(cr, uid, [aml.id], {'ref': aml.ref or '' + now})
                for move in account_move_obj.browse(cr, uid, move_ids, context):
                    account_move_obj.write(cr, uid, [move.id], {'name': move.name + now}, context)
                    _logger.debug('FGF picking action pre copy %s ' % (move.id))
                    move_copy_id = account_move_obj.copy(cr, uid, move.id, context)
                    _logger.debug('FGF picking action post copy %s ' % (move.id))
                    account_move_obj.write(cr, uid, [move_copy_id], {'name': move.name + now + '*'}, context)
                    _logger.debug('FGF picking action post write %s ' % (move.id))
                    cr.execute("""update account_move_line
                                    set debit=credit, credit=debit,
                                    ref = ref||'*'
                                where move_id = %s;""" % (move_copy_id))
                    # rename attachments (reports)
            # for some reason datas_fname has .pdf.pdf extension
            report_ids = report_xml_obj.search(cr, uid, [('model', '=', 'stock.picking'), ('attachment', '!=', False)])
            for report in report_xml_obj.browse(cr, uid, report_ids, context):
                if report.attachment:
                    aname = report.attachment.replace('object', 'pick')
                    if eval(aname):
                        aname = eval(aname) + '.pdf'
                        attachment_ids = attachment_obj.search(cr, uid, [('res_model', '=', 'stock.picking'),
                                                                         ('datas_fname', '=', aname),
                                                                         ('res_id', '=', pick.id)])
                        for a in attachment_obj.browse(cr, uid, attachment_ids, context):
                            vals = {
                                'name': a.name.replace('.pdf', now + '.pdf'),
                                'datas_fname': a.datas_fname.replace('.pdf.pdf', now + '.pdf.pdf')
                            }
                            attachment_obj.write(cr, uid, a.id, vals, context)

            self.write(cr, uid, pick.id, {'state': 'draft'}, context)
            wf_service = netsvc.LocalService("workflow")

            wf_service.trg_delete(uid, 'stock.picking', pick.id, cr)
            wf_service.trg_create(uid, 'stock.picking', pick.id, cr)

            self.log_picking(cr, uid, ids, context=context)

        return True
