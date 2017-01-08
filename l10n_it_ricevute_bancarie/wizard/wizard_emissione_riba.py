# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Andrea Cometa.
#    Email: info@andreacometa.it
#    Web site: http://www.andreacometa.it
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

# -------------------------------------------------------
#        EMISSIONE RIBA
# -------------------------------------------------------


class emissione_riba(orm.TransientModel):
    _name = "riba.emissione"
    _description = "Emissione Ricevute Bancarie"
    _columns = {
        'configurazione': fields.many2one('riba.configurazione', 'Configurazione', required=True),
    }

    def crea_distinta(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        def create_rdl(conta, rd_id, date_maturity, partner_id, acceptance_account_id, bank_id=None, bank_riba_id=None):
            riba_line_vals = {
                'sequence': conta,
                'bank_id': bank_id,
                'distinta_id': rd_id,
                'due_date': date_maturity,
                'partner_id': partner_id,
                'state': 'draft',
                'acceptance_account_id': acceptance_account_id,
                'bank_riba_id': bank_riba_id,
            }
            return riba_distinta_line_obj.create(cr, uid, riba_line_vals, context=context)

        """
        Qui creiamo la distinta
        """
        wizard_obj = self.browse(cr, uid, ids, context)[0]
        active_ids = context and context.get('active_ids', [])
        riba_distinta_obj = self.pool['riba.distinta']
        riba_distinta_line_obj = self.pool['riba.distinta.line']
        riba_distinta_move_line_obj = self.pool['riba.distinta.move.line']
        move_line_obj = self.pool['account.move.line']

        # create distinta
        riba_vals = {
            'name': self.pool['ir.sequence'].get(cr, uid, 'seq.riba.distinta'),
            'config': wizard_obj.configurazione.id,
            'user_id': uid,
            'date_created': fields.date.context_today(cr, uid, context),
        }
        rd_id = riba_distinta_obj.create(cr, uid, riba_vals, context)

        # group by partner and due date
        grouped_lines = {}
        move_line_ids = move_line_obj.search(cr, uid, [('id', 'in', active_ids)], context=context)
        for move_line in move_line_obj.browse(cr, uid, move_line_ids, context=context):
            if move_line.partner_id.group_riba:
                if not grouped_lines.get((move_line.partner_id.id, move_line.date_maturity), False):
                    grouped_lines[(move_line.partner_id.id, move_line.date_maturity)] = []
                grouped_lines[(move_line.partner_id.id, move_line.date_maturity)].append(
                    move_line)

        # create lines
        conta = 1
        no_bank = []
        for move_line in move_line_obj.browse(cr, uid, move_line_ids, context=context):
            if not (move_line.partner_id.bank_riba_id or move_line.partner_id.bank_ids):
                if move_line.partner_id.name not in no_bank:
                    no_bank.append(move_line.partner_id.name)
                continue
        if no_bank:
            raise orm.except_orm('Attenzione!', 'Il cliente %s non ha la banca!!!' % '\n'.join(no_bank))

        for move_line in move_line_obj.browse(cr, uid, move_line_ids, context=context):
            if move_line.partner_id.bank_riba_id:
                bank_riba_id = move_line.partner_id.bank_riba_id
            elif move_line.partner_id.bank_ids:
                bank_riba_id = []
                bank_id = move_line.partner_id.bank_ids[0]
            if move_line.partner_id.group_riba:
                for key in grouped_lines:
                    if key[0] == move_line.partner_id.id and key[1] == move_line.date_maturity:
                        if bank_riba_id:
                            rdl_id = create_rdl(conta, rd_id, move_line.date_maturity, move_line.partner_id.id,
                                            wizard_obj.configurazione.acceptance_account_id.id, None, bank_riba_id.id)
                        else:
                            rdl_id = create_rdl(conta, rd_id, move_line.date_maturity, move_line.partner_id.id,
                                            wizard_obj.configurazione.acceptance_account_id.id, bank_id.id, None)
#                        total = 0.0
#                        invoice_date_group = ''
                        for grouped_line in grouped_lines[key]:
                            riba_distinta_move_line_obj.create(cr, uid, {
                                'riba_line_id': rdl_id,
                                'amount': grouped_line.residual,
                                'move_line_id': grouped_line.id,
                                }, context=context)
                        del grouped_lines[key]
                        break
            else:
                if bank_riba_id:
                    rdl_id = create_rdl(conta, rd_id, move_line.date_maturity, move_line.partner_id.id,
                                    wizard_obj.configurazione.acceptance_account_id.id, None, bank_riba_id.id)
                else:
                    rdl_id = create_rdl(conta, rd_id, move_line.date_maturity, move_line.partner_id.id,
                                    wizard_obj.configurazione.acceptance_account_id.id, bank_id.id, None)
                riba_distinta_move_line_obj.create(cr, uid, {
                    'riba_line_id': rdl_id,
                    'amount': move_line.residual,
                    'move_line_id': move_line.id,
                    }, context=context)

            conta += 1

        # ----- show distinta form
        mod_obj = self.pool['ir.model.data']
        res = mod_obj.get_object_reference(cr, uid, 'l10n_it_ricevute_bancarie', 'view_distinta_riba_form')
        res_id = res and res[1] or False,
        return {
            'name': 'Distinta',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res_id,
            'res_model': 'riba.distinta',
            'type': 'ir.actions.act_window',
            #'nodestroy': True,
            'target': 'current',
            'res_id': rd_id or False,
        }
