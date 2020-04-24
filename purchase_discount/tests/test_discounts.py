"""
    Copyright (C) 2020 Didotech S.r.l. (<http://www.didotech.com/>).

    python3 -m venv pyvenv3
    . pyvenv3/bin/activate
    pip install pytest
    pip install --upgrade pip
    pip install git+git://github.com/andreinl/oerplib.git@py3x#egg=oerplib
    pip install pytest-html

    pip install --upgrade git+git://github.com/andreinl/oerplib.git@py3x

    pytest -q test_discounts.py
    pytest –-html=report.html
"""

from conftest import oerp


class TestDiscounts:
    COST_PRICE = 2
    PARTNER_PRICE = -2

    def make_purchase_order(self, pricelist_id, product_id, qty, supplier_id):
        purchase_line_model = oerp.get('purchase.order.line')

        result = purchase_line_model.onchange_product_id(
            [], pricelist_id, product_id, qty,
            False,
            supplier_id, date_order=False, fiscal_position_id=False,
            date_planned=False,
            name=False, price_unit=False,
            notes=False, context=None
        )

        return purchase_line_model.onchange_product_id(
            [], pricelist_id, product_id, qty,
            result['value']['product_uom'],
            supplier_id, date_order=False, fiscal_position_id=False,
            date_planned=False,
            name=False, price_unit=result['value']['price_unit'],
            notes=False, context=None
        )

    def test_listprice(self, supplier, product, pricelist, uom):
        qty = 1

        # Cost Price
        result = self.make_purchase_order(
            pricelist(self.COST_PRICE).id, product().id, qty, supplier.id)
        assert result['value']['price_unit'] == product().standard_price

        # Partner section of the product form
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE).id, product().id, qty, supplier.id)
        assert not result['value']['price_unit']

        price = 110
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE).id,
            product(min_quantity=1, price=price, uom_po_id=uom().id).id, qty, supplier.id
        )
        assert result['value']['price_unit'] == price

    def test_listprice_cf10_no_discount(self, supplier, product, pricelist, uom):
        # 10 products in a package
        factor_inv = 10
        uom_po_id = uom(factor_inv).id

        qty = 1
        cf_price = product().standard_price * factor_inv
        result = self.make_purchase_order(
            pricelist(self.COST_PRICE, visible=True).id,
            product(uom_po_id=uom_po_id).id, qty, supplier.id)
        assert result['value']['price_unit'] == cf_price

        # Discount not visible in purchase order
        result = self.make_purchase_order(
            pricelist(self.COST_PRICE, visible=False).id,
            product().id, qty, supplier.id)
        assert result['value']['price_unit'] == cf_price

        # Partner section of the product form
        qty = 1
        price = 110
        cf_price = price * factor_inv

        # result = self.make_purchase_order(
        #     pricelist(self.PARTNER_PRICE, visible=True).id,
        #     product(qty, cf_price).id, qty, supplier.id)
        # assert result['value']['price_unit'] == cf_price

        # Discount Not visible in Purchase Order
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE, visible=False).id,
            product(qty, cf_price).id, qty, supplier.id)
        assert result['value']['price_unit'] == cf_price

        # Quantity lower than quantity discount
        qty_10 = 10
        price_10 = 90
        cf_price_10 = price_10 * qty_10
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE, visible=True).id,
            product(qty_10, cf_price_10).id, qty, supplier.id)
        assert result['value']['price_unit'] == cf_price

        qty = 12
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE, visible=True).id,
            product().id, qty, supplier.id)
        assert result['value']['price_unit'] == price_10 * factor_inv

    def test_listprice_discount25(self, supplier, product, pricelist, uom):
        # 10 products in a package

        uom_po_id = uom().id

        # Partner section of the product form
        qty = 1
        price = 110

        # Set discount 25%
        discount = 25
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE, string_discount=25, visible=True).id,
            product(qty, price, uom_po_id=uom_po_id).id, qty, supplier.id)
        assert result['value']['price_unit'] == price
        assert result['value']['discount'] == discount

        # Discount Not visible in Purchase Order
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE, string_discount=25, visible=False).id,
            product(qty, price).id, qty, supplier.id)
        assert result['value']['price_unit'] == price * (100 - discount) / 100

        # Quantity lower than quantity discount
        qty_10 = 10
        price_10 = 90
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE, string_discount=25, visible=True).id,
            product(qty_10, price_10).id, qty, supplier.id)
        assert result['value']['price_unit'] == price
        assert result['value']['discount'] == discount

        qty = 12
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE, string_discount=25, visible=True).id,
            product().id, qty, supplier.id)
        assert result['value']['price_unit'] == price_10
        assert result['value']['discount'] == discount

    def test_listprice_cf10_discount25(self, supplier, product, pricelist, uom):
        # 10 products in a package
        factor_inv = 10
        uom_po_id = uom(factor_inv).id

        # Partner section of the product form
        qty = 1
        price = 110
        cf_price = price * factor_inv

        # Set discount 25%
        discount = 25
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE, string_discount=25, visible=True).id,
            product(qty, cf_price, uom_po_id=uom_po_id).id, qty, supplier.id)
        assert result['value']['price_unit'] == cf_price
        assert result['value']['discount'] == discount

        # Discount Not visible in Purchase Order
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE, string_discount=25, visible=False).id,
            product(qty, cf_price).id, qty, supplier.id)
        assert result['value']['price_unit'] == price * factor_inv * (100 - discount) / 100

        # Quantity lower than quantity discount
        qty_10 = 10
        price_10 = 90
        cf_price_10 = price_10 * qty_10
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE, string_discount=25, visible=True).id,
            product(qty_10, cf_price_10).id, qty, supplier.id)
        assert result['value']['price_unit'] == cf_price
        assert result['value']['discount'] == discount

        qty = 12
        result = self.make_purchase_order(
            pricelist(self.PARTNER_PRICE, string_discount=25, visible=True).id,
            product().id, qty, supplier.id)
        assert result['value']['price_unit'] == cf_price_10
        assert result['value']['discount'] == discount
