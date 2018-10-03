# -*- encoding: utf-8 -*-
##############################################################################
#
# Product serial module for OpenERP
#    Copyright (C) 2008 Raphaël Valyi
#    Copyright (C) 2011 Anevia S.A. - Ability to group invoice lines
#              written by Alexis Demeaulte <alexis.demeaulte@anevia.com>
#    Copyright (C) 2011 Akretion - Ability to split lines on logistical units
#              written by Emmanuel Samyn
#    Copyright (C) 2013-2015 Didotech SRL
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
import hashlib
from openerp import netsvc
import decimal_precision as dp


class stock_move(orm.Model):
    _inherit = "stock.move"
    # We order by product name because otherwise, after the split,
    # the products are "mixed" and not grouped by product name any more
    _order = "picking_id, name, id"

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        default.update({
            'new_prodlot_code': False,
            'check_product_qty': 0,
            'line_check': False,
            })

        return super(stock_move, self).copy(cr, uid, id, default, context=context)

    def _get_prodlot_code(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for move in self.browse(cr, uid, ids):
            res[move.id] = move.prodlot_id and move.prodlot_id.name or False
        return res

    def _set_prodlot_code(self, cr, uid, ids, name, value, arg, context=None):
        if not value:
            return False

        if isinstance(ids, (int, long)):
            ids = [ids]

        for move in self.browse(cr, uid, ids, context=context):
            product_id = move.product_id.id
            ## This way, we are taking an existent prodlot_id and writing a new value in it's place!
            ## very dangerous!
            #existing_prodlot = move.prodlot_id
            #if existing_prodlot: #avoid creating a prodlot twice
            #    self.pool['stock.production.lot').write(cr, uid, existing_prodlot.id, {'name': value})
            #else:
            existing_prodlot_id = self.pool['stock.production.lot'].search(cr, uid, [('name', '=', value),
                                                                                     ('product_id', '=', product_id)])
            if not existing_prodlot_id:  # avoid creating a prodlot twice
                prodlot_id = self.pool['stock.production.lot'].create(cr, uid, {
                    'name': value,
                    'product_id': product_id,
                })
                move.write({'prodlot_id': prodlot_id})

    def _get_tracking_code(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for move in self.browse(cr, uid, ids):
            res[move.id] = move.tracking_id and move.tracking_id.name or False
        return res

    def _set_tracking_code(self, cr, uid, ids, name, value, arg, context=None):
        if not value: return False

        if isinstance(ids, (int, long)):
            ids = [ids]

        for move in self.browse(cr, uid, ids, context=context):
            # product_id = move.product_id.id
            existing_tracking = move.tracking_id
            if existing_tracking:  #avoid creating a tracking twice
                self.pool['stock.tracking'].write(cr, uid, existing_tracking.id, {'name': value})
            else:
                tracking_id = self.pool['stock.tracking'].create(cr, uid, {
                    'name': value,
                })
                move.write({'tracking_id': tracking_id})

    _columns = {
        'new_prodlot_code': fields.function(_get_prodlot_code, fnct_inv=_set_prodlot_code,
                                            method=True, type='char', size=64,
                                            string='Prodlot fast input', select=1
        ),
        'new_tracking_code': fields.function(_get_tracking_code, fnct_inv=_set_tracking_code,
                                             method=True, type='char', size=64,
                                             string='Tracking fast input', select=1
        ),
        'balance': fields.boolean('Balance'),
        'pallet_qty': fields.integer('Number Pallet'),
        'pallet_id': fields.many2one('product.ul', 'Pallet', domain=[('type', '=', 'pallet')]),
        'line_check': fields.boolean('Check'),
        'check_product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
        'check_product_uom': fields.many2one('product.uom', 'Unit of Measure'),
    }

    def action_done(self, cr, uid, ids, context=None):
        """
        If we autosplit moves without reconnecting them 1 by 1, at least when some move which has descendants is split
        The following situation would happen (alphabetical order is order of creation, initially b and a pre-exists, then a is split, so a might get assigned and then split too):
        Incoming moves b, c, d
        Outgoing moves a, e, f
        Then we have those links: b->a, c->a, d->a
        and: b->, b->e, b->f
        The following code will detect this situation and reconnect properly the moves into only: b->a, c->e and d->f
        """
        result = super(stock_move, self).action_done(cr, uid, ids, context)
        for move in self.browse(cr, uid, ids, context):
            if move.product_id.lot_split_type and move.move_dest_id and move.move_dest_id.id:
                cr.execute(
                    "select stock_move.id from stock_move_history_ids left join stock_move on stock_move.id = stock_move_history_ids.child_id where parent_id=%s and stock_move.product_qty=1",
                    (move.id,))
                unitary_out_moves = cr.fetchall()
                if unitary_out_moves and len(unitary_out_moves) > 1:
                    unitary_in_moves = []
                    out_node = False
                    counter = 0
                    while len(unitary_in_moves) != len(unitary_out_moves) and counter < len(unitary_out_moves):
                        out_node = unitary_out_moves[counter][0]
                        cr.execute(
                            "select stock_move.id from stock_move_history_ids left join stock_move on stock_move.id = stock_move_history_ids.parent_id where child_id=%s and stock_move.product_qty=1",
                            (out_node,))
                        unitary_in_moves = cr.fetchall()
                        counter += 1

                    if len(unitary_in_moves) == len(unitary_out_moves):
                        unitary_out_moves.reverse()
                        unitary_out_moves.pop()
                        unitary_in_moves.reverse()
                        unitary_in_moves.pop()
                        counter = 0
                        for unitary_in_move in unitary_in_moves:
                            cr.execute("delete from stock_move_history_ids where parent_id=%s and child_id=%s",
                                       (unitary_in_moves[counter][0], out_node))
                            cr.execute(
                                "update stock_move_history_ids set parent_id=%s where parent_id=%s and child_id=%s",
                                (unitary_in_moves[counter][0], move.id, unitary_out_moves[counter][0]))
                            counter += 1

        return result

    def split_move(self, cr, uid, ids, context=None):
        lot_obj = self.pool['stock.production.lot']

        moves = self.browse(cr, uid, ids, context=context)
        if moves:
            auto_assign_lot = moves[0].picking_id.company_id.auto_assign_lot
        else:
            auto_assign_lot = True
        all_ids = list(ids)
        for move in moves:
            qty = move.product_qty
            lu_qty = False
            if move.product_id.lot_split_type == 'lu':
                if not move.product_id.packaging:
                    raise orm.except_orm(_('Error :'), _(
                        "Product '%s' has 'Lot split type' = 'Logistical Unit' but is missing packaging information.") % (
                                             move.product_id.name))
                lu_qty = move.product_id.packaging[0].qty

            elif move.product_id.lot_split_type == 'single':
                lu_qty = 1

            if lu_qty and qty >= 1:
                # Set existing move to LU quantity
                # search also product_lot

                vals = {
                    'product_qty': lu_qty,
                    'product_uos_qty': move.product_id.uos_coeff
                }
                # PROVO AD ATTRIBUIRE I NUMERI DI SERIE IN AUTOMATICO
                ##################### CARLO NON È CORRETTO ANDREBBE FATTO NON DENTRO QUESTO CICLO MA FUORI (DOPO) CHE VADO A SISTEMARE LE COSE PER IL LOTTO DI PRODUZIONE
                ####### ORA È SOLO UN TEST
                ##################### 8/8/2015
                prod_lot_ids = []
                index_lot = 0
                if move.picking_id.type == 'out' and move.product_id.track_outgoing and auto_assign_lot and not move.prodlot_id:
                    prod_lot_ids = lot_obj.search(cr, uid, [('product_id', '=', move.product_id.id),
                                                            ('stock_available', '>', 0)], order="date asc",
                                                  context=context)
                    if prod_lot_ids:
                        vals['prodlot_id'] = prod_lot_ids[index_lot]
                        if move.product_id.lot_split_type == 'single':
                            index_lot += 1

                self.write(cr, uid, move.id, vals, context)
                qty -= lu_qty
                # While still enough qty to create a new move, create it
                while qty >= lu_qty:
                    vals = {
                        'state': move.state,
                        'prodlot_id': None
                    }
                    if len(prod_lot_ids) > index_lot:
                        vals['prodlot_id'] = prod_lot_ids[index_lot]
                        if move.product_id.lot_split_type == 'single':
                            index_lot += 1

                    all_ids.append(self.copy(cr, uid, move.id, vals, context))
                    qty -= lu_qty

                # Create a last move for the remainder qty
                if qty > 0:
                    all_ids.append(
                        self.copy(cr, uid, move.id, {'state': move.state, 'prodlot_id': None, 'product_qty': qty},
                                  context))
        return all_ids

    def create(self, cr, user, vals, context=None):
        # For some reason we don't receive 'name', so we should create it:
        if ('name' not in vals) or (vals.get('name') == '/'):
            product = self.pool['product.product'].browse(cr, user, vals['product_id'], context=context)
            if product.default_code:
                vals['name'] = '[%s] %s' % (product.default_code, product.name)
            else:
                vals['name'] = product.name

        return super(stock_move, self).create(cr, user, vals, context)


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def action_assign_wkf(self, cr, uid, ids):
        result = super(stock_picking, self).action_assign_wkf(cr, uid, ids)

        for picking in self.browse(cr, uid, ids):
            if picking.company_id.autosplit_is_active:
                for move in picking.move_lines:
                    # Auto split
                    if ((move.product_id.track_production and move.location_id.usage == 'production') or \
                                (move.product_id.track_production and move.location_dest_id.usage == 'production') or \
                                (move.product_id.track_incoming and move.location_id.usage == 'supplier') or \
                                (move.product_id.track_outgoing and move.location_dest_id.usage == 'customer')):
                        self.pool['stock.move'].split_move(cr, uid, [move.id])

        return result

    # Because stock move line can be splitted by the module, we merge
    # invoice lines (if option 'is_group_invoice_line' is activated for the company)
    # at the following conditions :
    #   - the product is the same and
    #   - the discount is the same and
    #   - the unit price is the same and
    #   - the description is the same and
    #   - taxes are the same
    #   - they are from the same sale order lines (requires extra-code)
    # we merge invoice line together and do the sum of quantity and
    # subtotal.

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
                              group=False, type='out_invoice', context=None):
        invoice_dict = super(stock_picking, self).action_invoice_create(cr, uid,
                                                                        ids, journal_id, group, type, context=context)
        invoice_ids = []
        for picking_key in invoice_dict:
            invoice_ids.append(invoice_dict[picking_key])

        for invoice in self.pool['account.invoice'].browse(cr, uid, list(set(invoice_ids)), context=context):
            if not invoice.company_id.is_group_invoice_line:
                continue

            new_line_list = {}

            for line in invoice.invoice_line:

                # Build a key
                key = unicode(line.product_id.id) + ";" \
                      + unicode(line.discount) + ";" \
                      + unicode(line.price_unit) + ";" \
                      + line.name + ";"

                # Add the tax key part
                tax_tab = []
                for tax in line.invoice_line_tax_id:
                    tax_tab.append(tax.id)
                tax_tab.sort()
                for tax in tax_tab:
                    key = key + unicode(tax) + ";"

                # Add the sale order line part but check if the field exist because
                # it's install by a specific module (not from addons)
                if self.pool['ir.model.fields'].search(cr, uid, [('name', '=', 'sale_order_lines'),
                                                                 ('model', '=', 'account.invoice.line')],
                                                       context=context):
                    order_line_tab = []
                    for order_line in line.sale_order_lines:
                        order_line_tab.append(order_line.id)
                    order_line_tab.sort()
                    for order_line in order_line_tab:
                        key = key + unicode(order_line) + ";"

                # Get the hash of the key
                hash_key = hashlib.sha224(key.encode('utf8')).hexdigest()

                # if the key doesn't already exist, we keep the invoice line
                # and we add the key to new_line_list
                if hash_key not in new_line_list:
                    new_line_list[hash_key] = {
                        'id': line.id,
                        'quantity': line.quantity,
                        'price_subtotal': line.price_subtotal,
                    }
                # if the key already exist, we update new_line_list and 
                # we delete the invoice line
                else:
                    new_line_list[hash_key]['quantity'] = new_line_list[hash_key]['quantity'] + line.quantity
                    new_line_list[hash_key]['price_subtotal'] = new_line_list[hash_key]['price_subtotal'] \
                                                                + line.price_subtotal
                    self.pool['account.invoice.line'].unlink(cr, uid, line.id, context=context)

            # Write modifications made on invoice lines
            for hash_key in new_line_list:
                line_id = new_line_list[hash_key]['id']
                del new_line_list[hash_key]['id']
                self.pool['account.invoice.line'].write(cr, uid, line_id, new_line_list[hash_key], context=context)

        return invoice_dict

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool['stock.move']
        product_obj = self.pool['product.product']
        currency_obj = self.pool['res.currency']
        uom_obj = self.pool['product.uom']
        sequence_obj = self.pool['ir.sequence']
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s' % move.id, {})
                product_qty = partial_data.get('product_qty', 0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom', False)
                product_price = partial_data.get('product_price', 0.0)
                product_currency = partial_data.get('product_currency', False)
                prodlot_id = partial_data.get('prodlot_id', False)
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty,
                                                            move.product_uom.id)

                if move.product_qty == partial_qty[move.id] or partial_data.get('balance', False):
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id, context)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    if product.id in product_avail:
                        product_avail[product.id] += qty
                    else:
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        # new_price = currency_obj.compute(cr, uid, product_currency,
                        #                                 move_currency_id, product_price, context=context)
                        # new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                        #                                   product.uom_id.id, context=context)
                        new_price = move.price_unit
                        if product.qty_available <= 0:
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            new_std_price = ((amount_unit * product_avail[product.id]) \
                                             + (new_price * qty)) / (product_avail[product.id] + qty)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price}, context)

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        # move_obj.write(cr, uid, [move.id],
                        #                {'price_unit': product_price,
                        #                 'price_currency_id': product_currency}, context)

            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking:
                    new_picking = self.copy(cr, uid, pick.id,
                                            {
                                                'name': sequence_obj.get(cr, uid, 'stock.picking.%s' % pick.type),
                                                'move_lines': [],
                                                'state': 'draft',
                                            }, context)
                if product_qty != 0:
                    defaults = {
                        'product_qty': product_qty,
                        'product_uos_qty': product_qty,  # TODO: put correct uos_qty
                        'picking_id': new_picking,
                        'state': 'assigned',
                        'move_dest_id': False,
                        'price_unit': move.price_unit,
                        'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults, context)
                move_obj.write(cr, uid, [move.id],
                               {
                                   'product_qty': move.product_qty - partial_qty[move.id],
                                   'product_uos_qty': move.product_qty - partial_qty[move.id],
                                   # TODO: put correct uos_qty
                               }, context)

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking}, context)
            for move in complete:
                partial_data = partial_datas.get('move%s' % (move.id), {})
                defaults = {
                    'product_uom': product_uoms[move.id],
                    'product_qty': move_product_qty[move.id],
                    'balance': True,  # if complete then i force to close line CARLO partial_data.get('balance'),
                    'pallet_qty': partial_data.get('pallet_qty'),
                    'pallet_id': partial_data.get('pallet_id'),
                }
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})

                move_obj.write(cr, uid, [move.id], defaults, context)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty': product_qty,
                    'product_uos_qty': product_qty,  # TODO: put correct uos_qty
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults, context)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking], context)
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
            else:
                self.action_move(cr, uid, [pick.id], context)
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            # delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = delivered_pack_id

        return res


class stock_production_lot(orm.Model):
    _inherit = "stock.production.lot"

    def _last_location_id(self, cr, uid, ids, field_name, arg, context={}):
        """Retrieves the last location where the product with given serial is.
        Instead of using dates we assume the product is in the location having the
        highest number of products with the given serial (should be 1 if no mistake). This
        is better than using move dates because moves can easily be encoded at with wrong dates."""
        res = {}

        for prodlot_id in ids:
            cr.execute(
                "select location_dest_id " \
                "from stock_move inner join stock_report_prodlots on stock_report_prodlots.location_id = location_dest_id and stock_report_prodlots.prodlot_id = %s " \
                "where stock_move.prodlot_id = %s and stock_move.state=%s " \
                "order by stock_report_prodlots.qty DESC ",
                (prodlot_id, prodlot_id, 'done'))
            results = cr.fetchone()

            #TODO return tuple to avoid name_get being requested by the GTK client
            res[prodlot_id] = results and results[0] or False

        return res

    _columns = {
        'last_location_id': fields.function(_last_location_id, method=True,
                                            type="many2one", relation="stock.location",
                                            string="Last location",
                                            help="Display the current stock location of this production lot"),
    }

    def _check_name_unique(self, cr, uid, ids, context=None):
        #        if len(ids) == 1:
        #            lot = self.browse(cr, uid, ids[0])
        #            lot_name = self.name_get(cr, uid, ids, context=context)[0][1]
        #            lot_ids = self.name_search(cr, uid, lot_name, operator='=', context=context)
        #            if len(lot_ids) == 1:
        #                return True
        #            else:
        #                print '####### Duplicate serial number ########'
        #                import pdb; pdb.set_trace()
        #                return False
        #
        #
        #        return False
        return True

    #
    _constraints = [
        (_check_name_unique, _('Duplicate serial number'), ['name', 'product_id'])
    ]
