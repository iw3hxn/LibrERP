# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2012 Associazione OpenERP Italia
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
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class stock_picking(orm.Model):
    _inherit = "stock.picking"
    _columns = {
        'ddt_number': fields.char('DDT', size=64),
        'ddt_date': fields.date('DDT date', states={'done': [('readonly', True)]}),
        'ddt_in_reference': fields.char('In DDT', size=32),
        'ddt_in_date': fields.date('In DDT Date'),
        'cig': fields.char('CIG', size=64, help="Codice identificativo di gara"),
        'cup': fields.char('CUP', size=64, help="Codice unico di Progetto")
    }

    def name_get(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = []
        for picking in self.read(cr, uid, ids, ['id', 'ddt_number', 'ddt_in_reference', 'name', 'state'], context):
            picking_name = picking['ddt_number'] or picking['ddt_in_reference'] or picking['name']
            if picking['state'] != 'done':
                picking_name = '* ' + picking_name
            res.append((picking['id'], picking_name))
        return res

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):

        if not args:
            args = []

        if name:
            for column in ('ddt_number', 'origin', 'name', 'ddt_in_reference'):
                ids = self.search(cr, user, [(column, '=', name)] + args, limit=limit, context=context)
                if ids:
                    break

            if not len(ids):
                if len(name) == 1 and operator == 'ilike':
                    operator = '=ilike'
                    name = name + '%'

                domain = [
                        '|', '|', '|',
                        ('ddt_number', operator, name),
                        ('origin', operator, name),
                        ('name', operator, name),
                        ('ddt_in_reference', operator, name)
                    ]

                ids = self.search(cr, user, args + domain, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
        
    def _check_ddt_in_reference_unique(self, cr, uid, ids, context=None):
        # qui và cercato da gli stock.picking quelli che hanno ddt_in_reference e partner_id uguali
        return True

    _constraints = [(_check_ddt_in_reference_unique, 'Error! For a Partner must be only one DDT reference for year.', ['ddt_in_reference', 'partner_id'])]  

    #-----------------------------------------------------------------------------
    # EVITARE LA COPIA DI 'NUMERO DDT'
    #-----------------------------------------------------------------------------
    def copy(self, cr, uid, ids, default={}, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        default = default or {}
        default.update({
            'ddt_number': '',
            'ddt_in_reference': '',
            'cig': '',
            'cup': '',
        })
        if 'ddt_date' not in default:
            default.update({
                'ddt_date': False
            })
        if 'ddt_in_date' not in default:
            default.update({
                'ddt_in_date': False
            })
        if 'cig' not in default:
            default.update({
                'cig': False
            })
        if 'cup' not in default:
            default.update({
                'cup': False
            })

        return super(stock_picking, self).copy(cr, uid, ids, default, context)

    def action_ddt_assign(self, cr, uid, ids, context):
        wizard_assig_ddt_obj = self.pool['wizard.assign.ddt']
        for picking in self.read(cr, uid, ids, ['ddt_number', 'type'], context=context):
            if picking['ddt_number']:
                raise orm.except_orm(_('Error'),
                                     (_('Picking have Just DDT number {number}').format(number=picking.ddt_number)))
            if picking['type'] != 'out':
                raise orm.except_orm(_('Error'),
                                     (_('Only Out Picking can have DDT number')))
            ctx = context.copy()
            ctx['active_ids'] = [picking['id']]
            wizard_id = wizard_assig_ddt_obj.create(cr, uid, {}, ctx)
            wizard_assig_ddt_obj.assign_ddt(cr, uid, [wizard_id], context=ctx)
        return True

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        invoice_vals = super(stock_picking, self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context)
        invoice_vals.update({
            'cig': picking.cig,
            'cup': picking.cup,
        })
        return invoice_vals

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        # adaptative function: the system learn
        if vals.get('carriage_condition_id', False) or vals.get('goods_description_id', False):
            for picking in self.browse(cr, uid, ids, context):
                partner_vals = {}
                if not picking.partner_id.carriage_condition_id:
                    partner_vals['carriage_condition_id'] = vals.get('carriage_condition_id')
                if not picking.partner_id.goods_description_id:
                    partner_vals['goods_description_id'] = vals.get('goods_description_id')
                if partner_vals:
                    self.pool['res.partner'].write(cr, uid, [picking.partner_id.id], partner_vals, context)
        if vals.get('ddt_number') and vals['ddt_number'] == '' and not context.get('no_recovery', False):
            for picking in self.browse(cr, uid, ids, context):
                sequence_id = picking.stock_journal_id.ddt_sequence and \
                              picking.stock_journal_id.ddt_sequence.id or False
                if not sequence_id:
                    sequence_ids = self.pool['ir.sequence'].search(cr, uid, [('code', '=', 'stock.ddt')])
                    sequence_id = sequence_ids[0]

                self.pool['ir.sequence_recovery'].set(cr, uid, [picking.id], 'stock.picking', 'ddt_number', '', sequence_id)

        return super(stock_picking, self).write(cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        if not context.get('no_recovery', False):
            for picking in self.browse(cr, uid, ids, context):
                sequence_id = picking.stock_journal_id.ddt_sequence and \
                              picking.stock_journal_id.ddt_sequence.id or False
                if not sequence_id:
                    sequence_ids = self.pool['ir.sequence'].search(cr, uid, [('code', '=', 'stock.ddt')])
                    sequence_id = sequence_ids[0]

                self.pool['ir.sequence_recovery'].set(cr, uid, [picking.id], 'stock.picking', 'ddt_number', '', sequence_id)
        return super(stock_picking, self).unlink(cr, uid, ids, context)

    def _get_group_keys(self, cr, uid, partner, picking, context=None):
        res = super(stock_picking, self)._get_group_keys(cr, uid, partner, picking, context)
        if picking.cig:
            res = '{0}_CIG{1}'.format(res, picking.cig)
        if picking.cup:
            res = '{0}_CUP{1}'.format(res, picking.cup)
        return res
