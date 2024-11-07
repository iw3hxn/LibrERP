# -*- coding: utf-8 -*-
import logging

# from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

from openerp.addons.l10n_it_ade.bindings import fatturapa_v_1_2_1 as fattpa
from openerp.addons.l10n_it_ade.bindings.fatturapa_v_1_2_1 import (
    AltriDatiGestionaliType
)
from openerp.osv import orm


class WizardExportFatturapa(orm.TransientModel):
    _inherit = "wizard.export.fatturapa"

    def _export_fatturapa_external(self, cr, uid, inv, context):
        invoice_line_model = self.pool['account.invoice.line']
        xml_string = inv.fatturapa_attachment_in_id.datas.decode('base64')
        fatturapa = fattpa.CreateFromDocument(xml_string)
        FatturaBody = fatturapa.FatturaElettronicaBody[0]
        for line in FatturaBody.DatiBeniServizi.DettaglioLinee:
            line_ids = invoice_line_model.search(cr, uid,
                                                 [('name', '=', line.Descrizione), ('invoice_id', '=', inv.id)],
                                                 limit=1)
            if line_ids:
                invoice_line = invoice_line_model.browse(cr, uid, line_ids[0], context=context)
                external_code = invoice_line.account_id.external_code
                if not external_code:
                    external_code = 9999
                AltriDatiGestionali = AltriDatiGestionaliType(TipoDato='MASTRO', RiferimentoTesto=external_code)
                line.AltriDatiGestionali.append(AltriDatiGestionali)

        number = inv.fatturapa_attachment_in_id.name
        return number, fatturapa