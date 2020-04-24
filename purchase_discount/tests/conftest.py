"""
config.py:

from dataclasses import dataclass

@dataclass
class Config:
    host: str
    protocol: str
    port: int
    user: str
    password: str
    db_name: str

config = Config(
    ...
)
"""

import pytest
import oerplib
import config


class OpenErp:
    def __init__(self, config):
        # Prepare the connection to the server
        self.oerp = oerplib.OERP(config.host, protocol=config.protocol, port=config.port)

        # Login (the object returned is a browsable record)
        user = self.oerp.login(config.user, config.password, config.db_name)

    def execute(self, *args, **kwargs):
        return self.oerp.execute(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.oerp.get(*args, **kwargs)


oerp = OpenErp(config.config)


@pytest.fixture(scope="module")
def supplier():
    partner_model = oerp.get('res.partner')
    partner_address_model = oerp.get('res.partner.address')
    partner_id = partner_model.create({
        'name': 'test_partner',
        'supplier': True,
        'address': ([0, False, {
            'type': 'default',
            'city': 'Padova'
        }],)
    })
    partner = partner_model.browse(partner_id)
    yield partner

    print('Partner teardown...')
    partner_address_model.unlink(partner.address.ids)
    partner_model.unlink([partner_id])


@pytest.fixture(scope="module")
def product(supplier):
    product_model = oerp.get('product.product')
    supplierinfo_model = oerp.get('product.supplierinfo')
    partnerinfo_model = oerp.get('pricelist.partnerinfo')
    product_id = product_model.create({
        'name': 'test_product',
        # 'cost_method': 'lpp',  # Last Purchase Price
        'cost_method': 'standard',  # Standard Price
        'standard_price': 120,
        'last_purchase_price': 120,
        # 'uom_id':
    })

    product = product_model.browse(product_id)

    supplierinfo_id = supplierinfo_model.create({
        'name': supplier.id,
        'product_id': product_id,
        'product_name': product.name,
        'min_qty': 0,
        'delay': 1
    })

    def _get_product(min_quantity=0, price=0, uom_po_id=False):
        if min_quantity > 0 and price > 0:
            partner_info_ids = partnerinfo_model.search([
                ('min_quantity', '=', min_quantity),
                ('suppinfo_id', '=', supplierinfo_id)
            ], limit=1)
            if not partner_info_ids:
                partnerinfo_model.create({
                    'min_quantity': min_quantity,
                    'price': price,
                    'suppinfo_id': supplierinfo_id
                })
            else:
                partnerinfo_model.write(partner_info_ids, {
                    'price': price
                })

        if uom_po_id:
            product_model.write(product_id, {
                'uom_po_id': uom_po_id
            })

        return product

    yield _get_product

    print('Product teardown...')
    product_model.unlink([product_id])


@pytest.fixture(scope="module")
def pricelist():
    pricelist_model = oerp.get('product.pricelist')
    pricelist_item_model = oerp.get('product.pricelist.item')
    pricelist_version_model = oerp.get('product.pricelist.version')
    pricelist_ids = pricelist_model.search([('type', '=', 'purchase')])
    pricelist = pricelist_model.browse(pricelist_ids[0])

    def _get_pricelist(base=2, string_discount=0, visible=True):
        """
        :param base: int 1/Public Price, 2/Cost Price, -2/Partner section of the Product form
        :param string_discount: str
        :param: visible: bool Discount is visible in Purchase Order
        :return: pricelist
        """
        pricelist_model.write(pricelist.id, {
            'visible_discount': visible
        })
        pricelist_version = pricelist_version_model.browse(pricelist.version_id.ids[0])
        # pricelist_item = pricelist_item_model.browse(pricelist_version.items_id.ids[0])
        # ids = False, not used
        discount = pricelist_item_model.Calcolo_Sconto(False, str(string_discount))
        pricelist_item_model.write(pricelist_version.items_id.ids, {
            'base': base,
            'string_discount': str(string_discount),
            'price_discount': discount['value']['price_discount']
        })
        return pricelist

    return _get_pricelist


@pytest.fixture(scope="module")
def uom():
    uom_model = oerp.get('product.uom')
    uoms_to_delete = []

    def _get_uom(factor_inv=1):
        default_uom_id = 1
        default_uom = uom_model.browse(default_uom_id)
        if factor_inv == 1:
            uom = default_uom
        else:
            factor = 1 / factor_inv

            uom_ids = uom_model.search([
                ('category_id', '=', default_uom.category_id.id),
                ('factor', '=', factor),
                ('uom_type', '=', 'bigger')
            ], limit=1)
            if uom_ids:
                uom = uom_model.browse(uom_ids[0])
            else:
                uom_id = uom_model.create({
                    'category_id': default_uom.category_id.id,
                    'factor': factor,
                    'uom_type': 'bigger',
                    'name': f'CF {factor_inv} Pz',
                    'rounding': 1
                })
                uoms_to_delete.append(uom_id)
                uom = uom_model.browse(uom_id)

        return uom

    yield _get_uom
    print('UoM teardown...')
    if uoms_to_delete:
        uom_model.unlink(uoms_to_delete)
