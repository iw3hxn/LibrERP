# -*- coding: utf-8 -*-
# Copyright 2017-2018 - SHS-AV s.r.l. <http://wiki.zeroincombenze.org/it/Odoo>
#                       Associazione Odoo Italia <http://www.odoo-italia.org>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Generated Tue 2018-04-03 07:37:58 by pyxbgen.sh 0.1.5.5
# by Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>
#
import os
from . import vat_settlement_v_1_0
if os.environ.get('SPESOMETRO_VERSION', '2.1') == '2.0':
    from . import dati_fattura_v_2_0
else:
    from . import dati_fattura_v_2_1
from . import fatturapa_v_1_2
