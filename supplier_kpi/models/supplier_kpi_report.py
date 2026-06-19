# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2025 Didotech SRL
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

import logging
from openerp.osv import orm, fields
from openerp import tools

from .inherit_res_partner import SUPPLIER_TYPE_SELECTION

_logger = logging.getLogger(__name__)


class SupplierDelayReport(orm.Model):
    """
    One row per stock.move (type=in, state=done, ddt_in_date NOT NULL,
    purchase_line_id NOT NULL).  delay_days = ddt_in_date - date_planned.
    """
    _name = 'supplier.delay.report'
    _description = 'Supplier Delay Report'
    _auto = False
    _order = 'ddt_in_date desc'

    _columns = {
        'year': fields.char('Anno', size=4, readonly=True),
        'partner_id': fields.many2one('res.partner', 'Fornitore', readonly=True),
        'supplier_type': fields.selection(
            SUPPLIER_TYPE_SELECTION,
            'Classificazione QC',
            readonly=True,
        ),
        'order_id': fields.many2one('purchase.order', 'Ordine', readonly=True),
        'picking_id': fields.many2one('stock.picking', 'Picking', readonly=True),
        'product_id': fields.many2one('product.product', 'Prodotto', readonly=True),
        'date_planned': fields.date('Data prevista', readonly=True),
        'ddt_in_date': fields.date('Data DDT in', readonly=True),
        'ordered_qty': fields.float(
            'Qta ordinata',
            digits=(16, 3),
            readonly=True,
            # Valore di riga d'ordine ripetuto sui move multipli della
            # stessa riga: in raggruppamento e' diagnostico, non un totale.
            group_operator='sum',
        ),
        'received_qty': fields.float(
            'Qta ricevuta',
            digits=(16, 3),
            readonly=True,
            group_operator='sum',
        ),
        'line_amount': fields.float(
            # Valore della merce RICEVUTA in questa entrata (sm.product_qty),
            # non dell'intera riga ordinata: evita il sovra-conteggio su
            # consegne parziali/multiple. SUM = valore realmente ricevuto.
            'Totale riga',
            digits=(16, 2),
            readonly=True,
            group_operator='sum',
        ),
        'order_amount': fields.float(
            'Totale ordine',
            digits=(16, 2),
            readonly=True,
            # In 6.1 il default e' 'sum': order_amount ripete l'imponibile
            # ordine su ogni riga/move, quindi 'avg' evita il doppio conteggio
            # (raggruppando per ordine restituisce il totale ordine corretto).
            group_operator='avg',
        ),
        'delay_days': fields.integer(
            'Ritardo (gg)',
            readonly=True,
            group_operator='avg',
        ),
        'late': fields.integer(
            'In ritardo',
            readonly=True,
            group_operator='sum',
        ),
        'nbr': fields.integer(
            '# Righe',
            readonly=True,
            group_operator='sum',
        ),
    }

    def init(self, cr):
        # Il totale riga e' l'imponibile della quantita' RICEVUTA in questa
        # entrata (sm.product_qty), non dell'intera riga ordinata. Lo sconto
        # (modulo purchase_discount) e' opzionale: supplier_kpi non ne dipende,
        # quindi rileviamo la colonna a runtime e adattiamo la formula.
        cr.execute("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'purchase_order_line'
              AND column_name = 'discount'
        """)
        if cr.fetchone():
            line_amount_sql = ("pol.price_unit * sm.product_qty "
                               "* (1 - COALESCE(pol.discount, 0) / 100.0)")
        else:
            line_amount_sql = "pol.price_unit * sm.product_qty"

        tools.drop_view_if_exists(cr, 'supplier_delay_report')
        cr.execute("""
            CREATE OR REPLACE VIEW supplier_delay_report AS (
                SELECT
                    sm.id,
                    to_char(sp.ddt_in_date, 'YYYY')         AS year,
                    po.partner_id,
                    rp.supplier_type                         AS supplier_type,
                    po.id                                    AS order_id,
                    sp.id                                    AS picking_id,
                    sm.product_id,
                    pol.date_planned::date                   AS date_planned,
                    sp.ddt_in_date::date                     AS ddt_in_date,
                    pol.product_qty                          AS ordered_qty,
                    sm.product_qty                           AS received_qty,
                    """ + line_amount_sql + """              AS line_amount,
                    po.amount_untaxed                        AS order_amount,
                    (sp.ddt_in_date::date - pol.date_planned::date)
                                                             AS delay_days,
                    CASE WHEN sp.ddt_in_date::date > pol.date_planned::date
                         THEN 1 ELSE 0 END                  AS late,
                    1                                        AS nbr
                FROM stock_move sm
                JOIN stock_picking sp     ON sm.picking_id = sp.id
                JOIN purchase_order_line pol ON sm.purchase_line_id = pol.id
                JOIN purchase_order po    ON pol.order_id = po.id
                JOIN res_partner rp       ON po.partner_id = rp.id
                LEFT JOIN stock_journal sj ON sp.stock_journal_id = sj.id
                WHERE sp.type = 'in'
                  AND sp.state = 'done'
                  AND sm.state = 'done'
                  AND sp.ddt_in_date IS NOT NULL
                  -- solo ricezioni di fornitura originarie: i rientri da
                  -- riparazione/reso (giornale NC oppure picking generato
                  -- dal wizard di reso, nome con suffisso -return) restano
                  -- agganciati alla riga d'ordine ma non sono consegne
                  AND sj.nonconformity IS NOT TRUE
                  AND sp.name NOT ILIKE '%-return%'
            )
        """)


class SupplierNonconformityReport(orm.Model):
    """
    One row per done stock.picking whose journal has nonconformity=True.
    When the journal also has nonconformity_check_note=True, only pickings
    whose note contains the word RMA (also as prefix, e.g. "RMA123") or the
    word "reso" (case-insensitive, word-boundary match) are included.
    """
    _name = 'supplier.nonconformity.report'
    _description = 'Supplier Nonconformity Report'
    _auto = False
    _order = 'date desc'

    _columns = {
        'year': fields.char('Anno', size=4, readonly=True),
        'partner_id': fields.many2one('res.partner', 'Fornitore', readonly=True),
        'stock_journal_id': fields.many2one('stock.journal', 'Causale', readonly=True),
        'type': fields.selection(
            [('out', 'Sending Goods'),
             ('in', 'Getting Goods'),
             ('internal', 'Internal')],
            'Tipo',
            readonly=True,
        ),
        'picking_name': fields.char('Picking', size=64, readonly=True),
        'date': fields.date('Data', readonly=True),
        'nbr': fields.integer(
            '# NC',
            readonly=True,
            group_operator='sum',
        ),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'supplier_nonconformity_report')
        cr.execute("""
            CREATE OR REPLACE VIEW supplier_nonconformity_report AS (
                SELECT
                    sp.id,
                    to_char(
                        COALESCE(
                            sp.ddt_in_date,
                            sp.date_done::date,
                            sp.date::date
                        ), 'YYYY'
                    )                                        AS year,
                    sp.partner_id,
                    sp.stock_journal_id,
                    sp.type,
                    sp.name                                  AS picking_name,
                    COALESCE(
                        sp.ddt_in_date,
                        sp.date_done::date,
                        sp.date::date
                    )                                        AS date,
                    1                                        AS nbr
                FROM stock_picking sp
                JOIN stock_journal sj ON sp.stock_journal_id = sj.id
                WHERE sj.nonconformity = TRUE
                  AND sp.state = 'done'
                  AND (
                      sj.nonconformity_check_note IS NOT TRUE
                      -- word-boundary match: "RMA 123"/"RMA123"/"Reso merce" si',
                      -- "Normale"/"preso"/"resoconto" no
                      OR sp.note ~* '\\mrma|\\mreso\\M'
                  )
            )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
