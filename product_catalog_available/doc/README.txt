1) Aggiornare le informazioni dell'azienda

    a) specificando <Nome Azienda> come "Report - Intestazione" (res_company -> rml_header1)
    b) impostare il logo della ditta, per i report.

2) Aggiornare il file

server/openerp/report/render/rml2pdf/__init__.py

   aggiungendo

import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0

from reportlab.pdfbase import pdfmetrics 
from reportlab.pdfbase.ttfonts import TTFont

import reportlab

enc = 'UTF-8'
