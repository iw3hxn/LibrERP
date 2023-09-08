# -*- coding: utf-8 -*-
import logging

# from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

from openerp.addons.l10n_it_ade.bindings.fatturapa_v_1_2_1 import (
    AltriDatiGestionaliType
)
from openerp.osv import orm


class WizardExportFatturapa(orm.TransientModel):
    _inherit = "wizard.export.fatturapa"
    def _set_AltriDatiGestionali_line(self, cr, uid, DettaglioLinea, line, context):
        res = super(WizardExportFatturapa, self)._set_AltriDatiGestionali_line(cr, uid, DettaglioLinea, line, context)
        if line.invoice_id.type in ['in_invoice', 'in_refund']:
            AltriDatiGestionali = AltriDatiGestionaliType(TipoDato='MASTRO', RiferimentoTesto=line.account_id.external_code or line.account_id.code)
            DettaglioLinea.AltriDatiGestionali.append(AltriDatiGestionali)
        return res

    def setDatiGeneraliDocumento(self, cr, uid, invoice, body, context=None):
        res = super(WizardExportFatturapa, self).setDatiGeneraliDocumento(cr, uid, invoice, body, context)
        if invoice.type in ['in_invoice', 'in_refund']:
            body.DatiGenerali.DatiGeneraliDocumento.Numero = invoice.supplier_invoice_number
        return res
