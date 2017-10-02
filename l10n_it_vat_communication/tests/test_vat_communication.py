# -*- coding: utf-8 -*-
#    Copyright (C) 2017    SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# [2017: SHS-AV s.r.l.] First version
#
from openerp.tests.common import TransactionCase
# from openerp import netsvc


UT_FISCALCODE = 'VGLNTN59H26B963V'
UT_CODICE_CARICA = '1'


class TestCommunication(TransactionCase):
    def env789(self, model):
        """Return model pool [7.0]"""
        return self.registry(model)

    def ref789(self, model):
        """Return reference id [7.0]"""
        return self.ref(model)

    def write789(self, model, id, values):
        """Write existent record [7.0]"""
        model_pool = self.registry(model)
        return model_pool.write(self.cr, self.uid, [id], values)

    def write_ref(self, xid, values):
        """Browse and write existent record"""
        obj = self.browse_ref(xid)
        return obj.write(values)

    def create789(self, model, values):
        """Create a new record for test [7.0]"""
        return self.env789(model).create(self.cr,
                                         self.uid,
                                         values)

    # def setUp(self):
    #     self.setup_company()

    def test_vat_communication(self):
        self.vat_communication_id = self.create789(
            'account.vat.communication',
            {'soggetto_codice_fiscale': UT_FISCALCODE,
             'codice_carica': UT_CODICE_CARICA})
        pass
