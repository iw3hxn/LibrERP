# -*- encoding: utf-8 -*-

from openerp import pooler

from openerp.addons.sale_order_requirement.post_install import set_default_value


def migrate(cr, version):
    """Post-install script.
    If version is not set, we are called at installation time."""
    if not version:
        return

    pool = pooler.get_pool(cr.dbname)
    set_default_value(cr, pool)
    return
