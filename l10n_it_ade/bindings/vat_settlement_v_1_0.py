# flake8: noqa
# -*- coding: utf-8 -*-
# Copyright 2017-2019 - SHS-AV s.r.l. <http://wiki.zeroincombenze.org/it/Odoo>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
import pyxb
if pyxb.__version__ == '1.2.4':
    from vat_settlement_v_1_0__1_2_4 import *
elif pyxb.__version__ == '1.2.5':
    from vat_settlement_v_1_0__1_2_5 import *
elif pyxb.__version__ == '1.2.6':
    from vat_settlement_v_1_0__1_2_6 import *
else:
    raise pyxb.PyXBVersionError('1.2.4 to 1.2.6')
