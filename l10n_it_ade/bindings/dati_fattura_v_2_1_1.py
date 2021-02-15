# flake8: noqa
# -*- coding: utf-8 -*-
# Copyright 2017-2019 - SHS-AV s.r.l. <http://wiki.zeroincombenze.org/it/Odoo>
# Copyright 2019-2021 - Didotech s.r.l. <http://didotech.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
import pyxb
if pyxb.__version__ == '1.2.4':
    from dati_fattura_v_2_1_1__1_2_4 import *
# elif pyxb.__version__ == '1.2.5':
#     from dati_fattura_v_2_1_1__1_2_5 import *
# elif pyxb.__version__ == '1.2.6':
#     from dati_fattura_v_2_1_1__1_2_6 import *
else:
    # raise pyxb.PyXBVersionError('1.2.4 to 1.2.6')
    raise pyxb.PyXBVersionError('1.2.4')
