# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2025 Didotech S.r.l.
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
"""
Tests for the supplier_kpi module.

Covers:
  - stock.journal nonconformity flag initialisation (init_nonconformity_flags)
  - supplier.delay.report SQL view
  - supplier.nonconformity.report SQL view
  - res.partner.supplier_type QC classification + delay report filter

All tests use TransactionCase (rollback per method).  Data is created inside
the transaction so the SQL views can read it without a COMMIT.
"""

import uuid

import openerp.tests.common as test_common


# ---------------------------------------------------------------------------
# Helper: shared fixture builder used across several test methods
# ---------------------------------------------------------------------------

def _search_read(model, cr, uid, domain, fields, order=None):
    """search()+read() — search_read() does not exist in OpenERP 6.1."""
    ids = model.search(cr, uid, domain, order=order) if order \
        else model.search(cr, uid, domain)
    return model.read(cr, uid, ids, fields)


def _make_supplier_and_address(cr, uid, partner_model, address_model, name):
    """Create a res.partner (supplier) and its default res.partner.address.

    base_address_contacts requires the default ("Sede Legale") address to be
    passed inline in the partner create() via the one2many 'address' field;
    creating it with a separate create() raises except_orm.
    """
    partner_id = partner_model.create(cr, uid, {
        'name': name,
        'supplier': True,
        'customer': False,
        'address': [(0, 0, {'type': 'default'})],
    })
    partner = partner_model.browse(cr, uid, partner_id)
    address_id = partner.address[0].id
    return partner_id, address_id


def _get_uom_unit(registry, cr, uid):
    """Return the id of the 'Unit(s)' UOM (product.product_uom_unit)."""
    imd = registry('ir.model.data')
    _, uom_id = imd.get_object_reference(cr, uid, 'product', 'product_uom_unit')
    return uom_id


def _get_purchase_pricelist(registry, cr, uid):
    """Return the id of the default purchase pricelist (purchase.list0)."""
    imd = registry('ir.model.data')
    _, pl_id = imd.get_object_reference(cr, uid, 'purchase', 'list0')
    return pl_id


def _get_stock_input_location(registry, cr, uid):
    """Return the id of the stock input location (stock.stock_location_stock)."""
    imd = registry('ir.model.data')
    _, loc_id = imd.get_object_reference(cr, uid, 'stock', 'stock_location_stock')
    return loc_id


def _get_stock_supplier_location(registry, cr, uid):
    """Return the id of the suppliers virtual location."""
    imd = registry('ir.model.data')
    _, loc_id = imd.get_object_reference(cr, uid, 'stock', 'stock_location_suppliers')
    return loc_id


def _make_product(registry, cr, uid):
    """Create a storable product for test purposes."""
    uom_id = _get_uom_unit(registry, cr, uid)
    # create product.product directly: via _inherits it creates its own
    # product.template (6.1 does not auto-create variants from templates)
    pp = registry('product.product')
    return pp.create(cr, uid, {
        'name': 'KPI Test Product',
        'type': 'product',
        'uom_id': uom_id,
        'uom_po_id': uom_id,
        'standard_price': 10.0,
        'purchase_ok': True,
    })


def _make_purchase_order(registry, cr, uid, partner_id, address_id,
                         product_id, date_planned, qty=1.0):
    """Create a draft purchase.order with one line and return (po_id, line_id)."""
    uom_id = _get_uom_unit(registry, cr, uid)
    pl_id = _get_purchase_pricelist(registry, cr, uid)
    loc_id = _get_stock_input_location(registry, cr, uid)

    po_model = registry('purchase.order')
    pol_model = registry('purchase.order.line')

    po_id = po_model.create(cr, uid, {
        # explicit unique name: without it purchase_no_gap.create() looks up a
        # sale.shop by warehouse and crashes when the PO has neither;
        # purchase_order_name_uniq is UNIQUE(name, company_id)
        'name': 'PO_KPI_TEST_%s' % uuid.uuid4().hex[:10],
        'partner_id': partner_id,
        'partner_address_id': address_id,
        'pricelist_id': pl_id,
        'location_id': loc_id,
    })

    line_id = pol_model.create(cr, uid, {
        'order_id': po_id,
        'name': 'KPI Test Line',
        'product_id': product_id,
        'product_qty': qty,
        'product_uom': uom_id,
        'price_unit': 10.0,
        'date_planned': date_planned,
    })

    return po_id, line_id


def _make_done_picking_in(registry, cr, uid, po_id, address_id, product_id,
                          line_id, ddt_in_date, note=None, journal_id=None,
                          name=None):
    """
    Create a stock.picking (type='in') with one stock.move and force
    both to state='done', setting ddt_in_date on the picking.

    Returns picking_id.
    """
    uom_id = _get_uom_unit(registry, cr, uid)
    src_loc = _get_stock_supplier_location(registry, cr, uid)
    dst_loc = _get_stock_input_location(registry, cr, uid)

    picking_model = registry('stock.picking')
    move_model = registry('stock.move')

    picking_vals = {
        'type': 'in',
        'address_id': address_id,
        'purchase_id': po_id,
        'ddt_in_date': ddt_in_date,
    }
    if note is not None:
        picking_vals['note'] = note
    if journal_id is not None:
        picking_vals['stock_journal_id'] = journal_id
    if name is not None:
        picking_vals['name'] = name

    picking_id = picking_model.create(cr, uid, picking_vals)

    move_model.create(cr, uid, {
        'name': 'KPI Test Move',
        'picking_id': picking_id,
        'product_id': product_id,
        'product_qty': 1.0,
        'product_uom': uom_id,
        'location_id': src_loc,
        'location_dest_id': dst_loc,
        'purchase_line_id': line_id,
        'state': 'done',
        'date': ddt_in_date + ' 12:00:00',
        'date_expected': ddt_in_date + ' 12:00:00',
    })

    picking_model.write(cr, uid, [picking_id], {'state': 'done'})
    return picking_id


# ===========================================================================
# Test suite 1 — stock.journal.init_nonconformity_flags
# ===========================================================================

class TestInitNonconformityFlags(test_common.TransactionCase):
    """
    Unit tests for stock.journal.init_nonconformity_flags().

    The method must flag journals by name (case-insensitive ilike):
      * nonconformity=True only: repair / replacement / made-for-replacement names
      * nonconformity=True AND nonconformity_check_note=True: return / reso names
    """

    def setUp(self):
        super(TestInitNonconformityFlags, self).setUp()
        self.journal_model = self.registry('stock.journal')

    def _create_journal(self, name):
        return self.journal_model.create(self.cr, self.uid, {'name': name})

    # -- nonconformity-only names (EN) ---------------------------------------

    def test_en_crepair_sets_nonconformity_only(self):
        # "C/Repair" must set nonconformity=True and leave check_note=False
        jid = self._create_journal('C/Repair')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertTrue(j.nonconformity,
                        'C/Repair must have nonconformity=True')
        self.assertFalse(j.nonconformity_check_note,
                         'C/Repair must NOT have nonconformity_check_note=True')

    def test_en_crepair_under_warranty_sets_nonconformity_only(self):
        # "C/repair under warranty" must set nonconformity=True only
        jid = self._create_journal('C/repair under warranty')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertTrue(j.nonconformity)
        self.assertFalse(j.nonconformity_check_note)

    def test_en_creplacement_under_warranty_sets_nonconformity_only(self):
        # "C/replacement under warranty" must set nonconformity=True only
        jid = self._create_journal('C/replacement under warranty')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertTrue(j.nonconformity)
        self.assertFalse(j.nonconformity_check_note)

    def test_en_made_for_replacement_sets_nonconformity_only(self):
        # "Made for Replacement" must set nonconformity=True only
        jid = self._create_journal('Made for Replacement')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertTrue(j.nonconformity)
        self.assertFalse(j.nonconformity_check_note)

    # -- nonconformity-only names (IT) ---------------------------------------

    def test_it_criparazione_sets_nonconformity_only(self):
        # "C/Riparazione" must set nonconformity=True only
        jid = self._create_journal('C/Riparazione')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertTrue(j.nonconformity)
        self.assertFalse(j.nonconformity_check_note)

    def test_it_criparazione_in_garanzia_sets_nonconformity_only(self):
        # "C/riparazione in garanzia" must set nonconformity=True only
        jid = self._create_journal('C/riparazione in garanzia')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertTrue(j.nonconformity)
        self.assertFalse(j.nonconformity_check_note)

    def test_it_csostituzione_in_garanzia_sets_nonconformity_only(self):
        # "C/sostituzione in garanzia" must set nonconformity=True only
        jid = self._create_journal('C/sostituzione in garanzia')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertTrue(j.nonconformity)
        self.assertFalse(j.nonconformity_check_note)

    def test_it_reso_per_sostituzione_sets_nonconformity_only(self):
        # "Reso per Sostituzione" must set nonconformity=True only (not check_note)
        jid = self._create_journal('Reso per Sostituzione')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertTrue(j.nonconformity)
        self.assertFalse(j.nonconformity_check_note)

    # -- nonconformity + check_note names ------------------------------------

    def test_en_return_sets_both_flags(self):
        # "Return" must set both nonconformity=True AND nonconformity_check_note=True
        jid = self._create_journal('Return')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertTrue(j.nonconformity,
                        'Return must have nonconformity=True')
        self.assertTrue(j.nonconformity_check_note,
                        'Return must have nonconformity_check_note=True')

    def test_en_return_to_vendor_sets_both_flags(self):
        # "Return to Vendor" must set both flags
        jid = self._create_journal('Return to Vendor')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertTrue(j.nonconformity)
        self.assertTrue(j.nonconformity_check_note)

    def test_it_reso_sets_both_flags(self):
        # "Reso" must set both flags
        jid = self._create_journal('Reso')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertTrue(j.nonconformity)
        self.assertTrue(j.nonconformity_check_note)

    def test_it_reso_a_fornitore_sets_both_flags(self):
        # "Reso a Fornitore" must set both flags
        jid = self._create_journal('Reso a Fornitore')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertTrue(j.nonconformity)
        self.assertTrue(j.nonconformity_check_note)

    # -- unrelated journal must not be touched --------------------------------

    def test_unrelated_journal_not_flagged(self):
        # A journal with a generic name must remain unflagged
        jid = self._create_journal('Generic Warehouse Journal')
        self.journal_model.init_nonconformity_flags(self.cr, self.uid)
        j = self.journal_model.browse(self.cr, self.uid, jid)
        self.assertFalse(j.nonconformity,
                         'Unrelated journal must NOT have nonconformity=True')
        self.assertFalse(j.nonconformity_check_note,
                         'Unrelated journal must NOT have nonconformity_check_note=True')


# ===========================================================================
# Test suite 2 — supplier.delay.report
# ===========================================================================

class TestSupplierDelayReport(test_common.TransactionCase):
    """
    Tests for the supplier.delay.report SQL view.

    The view must expose one row per stock.move done (type=in, state=done,
    ddt_in_date NOT NULL, purchase_line_id NOT NULL) with correct delay_days
    computation.
    """

    def setUp(self):
        super(TestSupplierDelayReport, self).setUp()
        self.report_model = self.registry('supplier.delay.report')
        self.partner_model = self.registry('res.partner')
        self.address_model = self.registry('res.partner.address')

        self.partner_id, self.address_id = _make_supplier_and_address(
            self.cr, self.uid, self.partner_model, self.address_model,
            'KPI Supplier Delay'
        )
        self.product_id = _make_product(self.registry, self.cr, self.uid)

    def test_delay_days_positive_when_late(self):
        # When ddt_in_date > date_planned the delay must be positive (late delivery)
        po_id, line_id = _make_purchase_order(
            self.registry, self.cr, self.uid,
            self.partner_id, self.address_id, self.product_id,
            date_planned='2025-01-10',
        )
        _make_done_picking_in(
            self.registry, self.cr, self.uid,
            po_id, self.address_id, self.product_id, line_id,
            ddt_in_date='2025-01-15',
        )

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('order_id', '=', po_id)],
            ['delay_days', 'late'],
        )
        self.assertEqual(len(rows), 1, 'Expected exactly 1 report row')
        self.assertEqual(rows[0]['delay_days'], 5,
                         'delay_days must be ddt_in_date - date_planned = 5')
        self.assertEqual(rows[0]['late'], 1,
                         'late must be 1 when delay_days > 0')

    def test_delay_days_negative_when_early(self):
        # When ddt_in_date < date_planned the delay must be negative (early delivery)
        po_id, line_id = _make_purchase_order(
            self.registry, self.cr, self.uid,
            self.partner_id, self.address_id, self.product_id,
            date_planned='2025-02-20',
        )
        _make_done_picking_in(
            self.registry, self.cr, self.uid,
            po_id, self.address_id, self.product_id, line_id,
            ddt_in_date='2025-02-15',
        )

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('order_id', '=', po_id)],
            ['delay_days', 'late'],
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['delay_days'], -5,
                         'delay_days must be negative for early delivery')
        self.assertEqual(rows[0]['late'], 0,
                         'late must be 0 when delay_days <= 0')

    def test_nc_journal_reception_excluded(self):
        # A re-reception on a nonconformity-flagged journal (goods coming back
        # from repair/return, e.g. journal "Return") stays linked to the PO
        # line but is NOT a supply delivery: it must not appear in the report
        # (real case: PO230057, original reception 2023, repair return 2024).
        po_id, line_id = _make_purchase_order(
            self.registry, self.cr, self.uid,
            self.partner_id, self.address_id, self.product_id,
            date_planned='2025-01-10',
        )
        journal_model = self.registry('stock.journal')
        nc_journal_id = journal_model.create(self.cr, self.uid, {
            'name': 'KPI Test Return Journal',
            'nonconformity': True,
        })
        _make_done_picking_in(
            self.registry, self.cr, self.uid,
            po_id, self.address_id, self.product_id, line_id,
            ddt_in_date='2025-06-30', journal_id=nc_journal_id,
        )

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('order_id', '=', po_id)],
            ['delay_days'],
        )
        self.assertEqual(len(rows), 0,
                         'Reception on NC-flagged journal must NOT appear '
                         'in the delay report')

    def test_return_wizard_picking_excluded(self):
        # Pickings created by the 6.1 return wizard get a "-return" suffix in
        # their name: they are re-receptions, not deliveries, and must be
        # excluded even when their journal is not NC-flagged.
        po_id, line_id = _make_purchase_order(
            self.registry, self.cr, self.uid,
            self.partner_id, self.address_id, self.product_id,
            date_planned='2025-01-10',
        )
        _make_done_picking_in(
            self.registry, self.cr, self.uid,
            po_id, self.address_id, self.product_id, line_id,
            ddt_in_date='2025-06-30',
            name='IN/99999-OUT/88888-KPI-test-return-return',
        )

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('order_id', '=', po_id)],
            ['delay_days'],
        )
        self.assertEqual(len(rows), 0,
                         'Picking named *-return must NOT appear in the '
                         'delay report')

    def test_picking_without_ddt_in_date_excluded(self):
        # A done picking-in with no ddt_in_date must NOT appear in the report
        po_id, line_id = _make_purchase_order(
            self.registry, self.cr, self.uid,
            self.partner_id, self.address_id, self.product_id,
            date_planned='2025-03-10',
        )
        # Create picking WITHOUT ddt_in_date
        uom_id = _get_uom_unit(self.registry, self.cr, self.uid)
        src_loc = _get_stock_supplier_location(self.registry, self.cr, self.uid)
        dst_loc = _get_stock_input_location(self.registry, self.cr, self.uid)

        picking_model = self.registry('stock.picking')
        move_model = self.registry('stock.move')

        picking_id = picking_model.create(self.cr, self.uid, {
            'type': 'in',
            'address_id': self.address_id,
            'purchase_id': po_id,
            # ddt_in_date intentionally omitted
        })
        move_model.create(self.cr, self.uid, {
            'name': 'No DDT Move',
            'picking_id': picking_id,
            'product_id': self.product_id,
            'product_qty': 1.0,
            'product_uom': uom_id,
            'location_id': src_loc,
            'location_dest_id': dst_loc,
            'purchase_line_id': line_id,
            'state': 'done',
            'date': '2025-03-10 12:00:00',
            'date_expected': '2025-03-10 12:00:00',
        })
        picking_model.write(self.cr, self.uid, [picking_id], {'state': 'done'})

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('order_id', '=', po_id)],
            ['delay_days'],
        )
        self.assertEqual(len(rows), 0,
                         'Picking without ddt_in_date must not appear in delay report')

    def test_partial_delivery_two_pickings_two_rows(self):
        # Same PO, 2 lines with different date_planned, 2 pickings with
        # different ddt_in_date → 2 independent rows with distinct delay_days
        uom_id = _get_uom_unit(self.registry, self.cr, self.uid)
        pl_id = _get_purchase_pricelist(self.registry, self.cr, self.uid)
        loc_id = _get_stock_input_location(self.registry, self.cr, self.uid)

        po_model = self.registry('purchase.order')
        pol_model = self.registry('purchase.order.line')

        po_id = po_model.create(self.cr, self.uid, {
            # see _make_purchase_order: explicit name skips purchase_no_gap
            'name': 'PO_KPI_TEST_%s' % uuid.uuid4().hex[:10],
            'partner_id': self.partner_id,
            'partner_address_id': self.address_id,
            'pricelist_id': pl_id,
            'location_id': loc_id,
        })

        line1_id = pol_model.create(self.cr, self.uid, {
            'order_id': po_id,
            'name': 'Line 1',
            'product_id': self.product_id,
            'product_qty': 1.0,
            'product_uom': uom_id,
            'price_unit': 10.0,
            'date_planned': '2025-04-01',
        })
        line2_id = pol_model.create(self.cr, self.uid, {
            'order_id': po_id,
            'name': 'Line 2',
            'product_id': self.product_id,
            'product_qty': 1.0,
            'product_uom': uom_id,
            'price_unit': 10.0,
            'date_planned': '2025-04-10',
        })

        # First delivery: 3 days late for line1
        _make_done_picking_in(
            self.registry, self.cr, self.uid,
            po_id, self.address_id, self.product_id, line1_id,
            ddt_in_date='2025-04-04',
        )
        # Second delivery: 5 days early for line2
        _make_done_picking_in(
            self.registry, self.cr, self.uid,
            po_id, self.address_id, self.product_id, line2_id,
            ddt_in_date='2025-04-05',
        )

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('order_id', '=', po_id)],
            ['delay_days'],
            order='delay_days asc',
        )
        self.assertEqual(len(rows), 2,
                         'Partial delivery: expected 2 report rows, one per picking/line')
        delays = sorted([r['delay_days'] for r in rows])
        self.assertEqual(delays, [-5, 3],
                         'First row: 3 days late; second row: 5 days early')

    def test_report_row_links_correct_partner(self):
        # partner_id in the report must match the PO partner
        po_id, line_id = _make_purchase_order(
            self.registry, self.cr, self.uid,
            self.partner_id, self.address_id, self.product_id,
            date_planned='2025-05-01',
        )
        _make_done_picking_in(
            self.registry, self.cr, self.uid,
            po_id, self.address_id, self.product_id, line_id,
            ddt_in_date='2025-05-03',
        )

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('order_id', '=', po_id)],
            ['partner_id'],
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['partner_id'][0], self.partner_id,
                         'partner_id in delay report must match the purchase order supplier')

    def test_year_column_derived_from_ddt_in_date(self):
        # The year column must be the 4-digit year string extracted from ddt_in_date
        po_id, line_id = _make_purchase_order(
            self.registry, self.cr, self.uid,
            self.partner_id, self.address_id, self.product_id,
            date_planned='2024-11-01',
        )
        _make_done_picking_in(
            self.registry, self.cr, self.uid,
            po_id, self.address_id, self.product_id, line_id,
            ddt_in_date='2024-11-05',
        )

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('order_id', '=', po_id)],
            ['year'],
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['year'], '2024',
                         'year must be the 4-digit string from ddt_in_date')


# ===========================================================================
# Test suite 2b — res.partner.supplier_type + delay report QC filter
# ===========================================================================

class TestSupplierTypeField(test_common.TransactionCase):
    """
    Tests for the res.partner.supplier_type selection field and its
    exposure/filterability on supplier.delay.report.
    """

    SUPPLIER_TYPES = ['QC_important', 'QC_primary', 'QC_secondary']

    def setUp(self):
        super(TestSupplierTypeField, self).setUp()
        self.report_model = self.registry('supplier.delay.report')
        self.partner_model = self.registry('res.partner')
        self.address_model = self.registry('res.partner.address')

    def test_supplier_type_accepts_all_qc_values(self):
        # Each of the 3 QC classification keys must be writable and read back
        for stype in self.SUPPLIER_TYPES:
            partner_id, _ = _make_supplier_and_address(
                self.cr, self.uid, self.partner_model, self.address_model,
                'KPI Supplier %s' % stype,
            )
            self.partner_model.write(self.cr, self.uid, [partner_id],
                                     {'supplier_type': stype})
            partner = self.partner_model.browse(self.cr, self.uid, partner_id)
            self.assertEqual(partner.supplier_type, stype)

    def test_supplier_type_defaults_to_false(self):
        # A new partner must have no QC classification
        partner_id, _ = _make_supplier_and_address(
            self.cr, self.uid, self.partner_model, self.address_model,
            'KPI Supplier unclassified',
        )
        partner = self.partner_model.browse(self.cr, self.uid, partner_id)
        self.assertFalse(partner.supplier_type)

    def test_supplier_type_rejects_invalid_value(self):
        # A value outside the selection must be refused by the ORM
        partner_id, _ = _make_supplier_and_address(
            self.cr, self.uid, self.partner_model, self.address_model,
            'KPI Supplier invalid type',
        )
        self.assertRaises(
            Exception,
            self.partner_model.write,
            self.cr, self.uid, [partner_id],
            {'supplier_type': 'QC_bogus'},
        )

    def _make_delay_row(self, partner_id, address_id):
        """PO + done picking-in 5 days late → 1 delay report row."""
        product_id = _make_product(self.registry, self.cr, self.uid)
        po_id, line_id = _make_purchase_order(
            self.registry, self.cr, self.uid,
            partner_id, address_id, product_id,
            date_planned='2025-01-10',
        )
        _make_done_picking_in(
            self.registry, self.cr, self.uid,
            po_id, address_id, product_id, line_id,
            ddt_in_date='2025-01-15',
        )
        return po_id

    def test_delay_report_exposes_supplier_type(self):
        # The report row of a classified supplier must carry its supplier_type
        partner_id, address_id = _make_supplier_and_address(
            self.cr, self.uid, self.partner_model, self.address_model,
            'KPI Supplier QC important',
        )
        self.partner_model.write(self.cr, self.uid, [partner_id],
                                 {'supplier_type': 'QC_important'})
        po_id = self._make_delay_row(partner_id, address_id)

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('order_id', '=', po_id)],
            ['supplier_type'],
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['supplier_type'], 'QC_important',
                         'Delay report row must expose the partner supplier_type')

    def test_delay_report_filter_on_supplier_type_set(self):
        # domain [('supplier_type','!=',False)] must include the classified
        # supplier rows and exclude the unclassified one
        classified_id, classified_addr = _make_supplier_and_address(
            self.cr, self.uid, self.partner_model, self.address_model,
            'KPI Supplier classified',
        )
        self.partner_model.write(self.cr, self.uid, [classified_id],
                                 {'supplier_type': 'QC_primary'})
        unclassified_id, unclassified_addr = _make_supplier_and_address(
            self.cr, self.uid, self.partner_model, self.address_model,
            'KPI Supplier not classified',
        )
        po_classified = self._make_delay_row(classified_id, classified_addr)
        po_unclassified = self._make_delay_row(unclassified_id, unclassified_addr)

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('order_id', 'in', [po_classified, po_unclassified]),
             ('supplier_type', '!=', False)],
            ['partner_id', 'supplier_type'],
        )
        self.assertEqual(len(rows), 1,
                         'Only the classified supplier row must pass the filter')
        self.assertEqual(rows[0]['partner_id'][0], classified_id)
        self.assertEqual(rows[0]['supplier_type'], 'QC_primary')

    def test_delay_report_filter_on_specific_type(self):
        # Filtering on a single QC class must return only that class
        important_id, important_addr = _make_supplier_and_address(
            self.cr, self.uid, self.partner_model, self.address_model,
            'KPI Supplier important only',
        )
        self.partner_model.write(self.cr, self.uid, [important_id],
                                 {'supplier_type': 'QC_important'})
        secondary_id, secondary_addr = _make_supplier_and_address(
            self.cr, self.uid, self.partner_model, self.address_model,
            'KPI Supplier secondary only',
        )
        self.partner_model.write(self.cr, self.uid, [secondary_id],
                                 {'supplier_type': 'QC_secondary'})
        po_important = self._make_delay_row(important_id, important_addr)
        po_secondary = self._make_delay_row(secondary_id, secondary_addr)

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('order_id', 'in', [po_important, po_secondary]),
             ('supplier_type', '=', 'QC_important')],
            ['partner_id'],
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['partner_id'][0], important_id)


# ===========================================================================
# Test suite 3 — supplier.nonconformity.report
# ===========================================================================

class TestSupplierNonconformityReport(test_common.TransactionCase):
    """
    Tests for the supplier.nonconformity.report SQL view.

    A picking is included when:
      - state='done'
      - stock_journal_id.nonconformity=True
      - if nonconformity_check_note=True: picking.note must match /(rma|reso)/i

    The view does NOT filter on picking.type.
    """

    def setUp(self):
        super(TestSupplierNonconformityReport, self).setUp()
        self.report_model = self.registry('supplier.nonconformity.report')
        self.journal_model = self.registry('stock.journal')
        self.partner_model = self.registry('res.partner')
        self.address_model = self.registry('res.partner.address')
        self.picking_model = self.registry('stock.picking')

        self.partner_id, self.address_id = _make_supplier_and_address(
            self.cr, self.uid, self.partner_model, self.address_model,
            'KPI Supplier NC'
        )
        self.product_id = _make_product(self.registry, self.cr, self.uid)

        # A journal flagged nonconformity=True, check_note=False
        self.j_nc_id = self.journal_model.create(self.cr, self.uid, {
            'name': 'NC Journal (no check note)',
            'nonconformity': True,
            'nonconformity_check_note': False,
        })
        # A journal flagged nonconformity=True, check_note=True
        self.j_nc_note_id = self.journal_model.create(self.cr, self.uid, {
            'name': 'NC Journal (check note)',
            'nonconformity': True,
            'nonconformity_check_note': True,
        })
        # A journal NOT flagged
        self.j_plain_id = self.journal_model.create(self.cr, self.uid, {
            'name': 'Plain Journal',
            'nonconformity': False,
            'nonconformity_check_note': False,
        })

    def _make_picking(self, journal_id, state='done', picking_type='out', note=None):
        """Create a minimal picking and force its state."""
        vals = {
            'type': picking_type,
            'address_id': self.address_id,
            'stock_journal_id': journal_id,
        }
        if note is not None:
            vals['note'] = note

        uom_id = _get_uom_unit(self.registry, self.cr, self.uid)
        src_loc = _get_stock_supplier_location(self.registry, self.cr, self.uid)
        dst_loc = _get_stock_input_location(self.registry, self.cr, self.uid)

        picking_id = self.picking_model.create(self.cr, self.uid, vals)

        move_model = self.registry('stock.move')
        move_model.create(self.cr, self.uid, {
            'name': 'NC Test Move',
            'picking_id': picking_id,
            'product_id': self.product_id,
            'product_qty': 1.0,
            'product_uom': uom_id,
            'location_id': src_loc,
            'location_dest_id': dst_loc,
            'state': 'done' if state == 'done' else 'confirmed',
            'date': '2025-06-01 12:00:00',
            'date_expected': '2025-06-01 12:00:00',
        })

        self.picking_model.write(self.cr, self.uid, [picking_id], {'state': state})
        return picking_id

    def test_picking_out_done_flagged_journal_included(self):
        # An OUT done picking with a flagged journal (no check_note) must appear
        picking_id = self._make_picking(self.j_nc_id, state='done', picking_type='out')
        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('stock_journal_id', '=', self.j_nc_id)],
            ['nbr'],
        )
        self.assertTrue(len(rows) > 0,
                        'Done picking with flagged journal must appear in NC report')

    def test_picking_with_check_note_and_rma_keyword_included(self):
        # journal check_note=True + note contains "RMA" keyword → must appear
        picking_id = self._make_picking(
            self.j_nc_note_id, state='done', picking_type='out',
            note='Pratica RMA 123',
        )
        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('stock_journal_id', '=', self.j_nc_note_id)],
            ['nbr'],
        )
        # Filter to this specific picking (by name if available, otherwise count > 0)
        self.assertTrue(len(rows) > 0,
                        'Picking with check_note journal and RMA keyword must appear in NC report')

    def test_picking_with_check_note_and_reso_keyword_included(self):
        # journal check_note=True + note contains "reso" (case-insensitive) → must appear
        picking_id = self._make_picking(
            self.j_nc_note_id, state='done', picking_type='in',
            note='Reso merce difettosa',
        )
        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('stock_journal_id', '=', self.j_nc_note_id)],
            ['nbr'],
        )
        self.assertTrue(len(rows) > 0,
                        'Picking with check_note journal and reso keyword must appear in NC report')

    def test_picking_with_check_note_and_no_keyword_excluded(self):
        # journal check_note=True + note WITHOUT rma/reso keyword → must NOT appear
        picking_id = self._make_picking(
            self.j_nc_note_id, state='done', picking_type='out',
            note='Normale consegna merce',
        )
        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('stock_journal_id', '=', self.j_nc_note_id),
             ('picking_name', '=', self.picking_model.browse(
                 self.cr, self.uid, picking_id).name)],
            ['nbr'],
        )
        self.assertEqual(len(rows), 0,
                         'Picking with check_note journal and no keyword must NOT appear in NC report')

    def test_picking_with_check_note_and_empty_note_excluded(self):
        # journal check_note=True + note empty/NULL → must NOT appear
        picking_id = self._make_picking(
            self.j_nc_note_id, state='done', picking_type='out',
            note=None,
        )
        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('stock_journal_id', '=', self.j_nc_note_id),
             ('picking_name', '=', self.picking_model.browse(
                 self.cr, self.uid, picking_id).name)],
            ['nbr'],
        )
        self.assertEqual(len(rows), 0,
                         'Picking with check_note journal and empty note must NOT appear in NC report')

    def test_picking_with_unflagged_journal_excluded(self):
        # A done picking with a non-flagged journal must NOT appear
        picking_id = self._make_picking(self.j_plain_id, state='done')
        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('stock_journal_id', '=', self.j_plain_id)],
            ['nbr'],
        )
        self.assertEqual(len(rows), 0,
                         'Done picking with non-flagged journal must NOT appear in NC report')

    def test_picking_draft_state_excluded(self):
        # A draft picking (state != done) must NOT appear, even with flagged journal
        picking_id = self._make_picking(self.j_nc_id, state='draft')
        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('stock_journal_id', '=', self.j_nc_id),
             ('picking_name', '=', self.picking_model.browse(
                 self.cr, self.uid, picking_id).name)],
            ['nbr'],
        )
        self.assertEqual(len(rows), 0,
                         'Draft picking must NOT appear in NC report')

    def test_nc_report_does_not_filter_on_picking_type(self):
        # The NC report must include both 'in' and 'out' done pickings with flagged journal
        picking_out = self._make_picking(self.j_nc_id, state='done', picking_type='out')
        picking_in = self._make_picking(self.j_nc_id, state='done', picking_type='in')

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('stock_journal_id', '=', self.j_nc_id)],
            ['type'],
        )
        types_found = set(r['type'] for r in rows)
        self.assertIn('out', types_found,
                      'NC report must include out-type pickings')
        self.assertIn('in', types_found,
                      'NC report must include in-type pickings')

    def test_nc_report_year_from_picking_date(self):
        # The year column must be extracted from the picking date
        picking_id = self._make_picking(self.j_nc_id, state='done', picking_type='out')
        # Force the picking date to a known value after creation
        self.picking_model.write(self.cr, self.uid, [picking_id],
                                 {'date': '2023-07-15 10:00:00'})

        rows = _search_read(self.report_model,
            self.cr, self.uid,
            [('stock_journal_id', '=', self.j_nc_id),
             ('picking_name', '=', self.picking_model.browse(
                 self.cr, self.uid, picking_id).name)],
            ['year'],
        )
        self.assertTrue(len(rows) > 0)
        self.assertEqual(rows[0]['year'], '2023',
                         'year must be the 4-digit string from picking date')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
