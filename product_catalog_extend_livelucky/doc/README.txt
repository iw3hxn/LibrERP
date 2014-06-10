1) Aggiornare le informazioni dell'azienda

    a) specificando "LIVELUCKY" come "Report - Intestazione" (res_company -> rml_header1)
    b) sostituendo il logo preesistente con quello nuovo.

2) Installare il font "BlairMdITC_TT_Medium.ttf" nel percorso dei font di sistema

/usr/share/fonts/truetype

3) Aggiornare il file

server/bin/report/render/rml2pdf/__init__.py

   aggiungendo

import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0

from reportlab.pdfbase import pdfmetrics 
from reportlab.pdfbase.ttfonts import TTFont

import reportlab

enc = 'UTF-8'

pdfmetrics.registerFont(TTFont('BlairMdITC_TT_Medium', 'BlairMdITC_TT_Medium.ttf', enc))
#pdfmetrics.registerFont(TTFont('BlairMdITC_TT_Medium-Bold', 'BlairMdITC_TT_Medium-Bold.ttf', enc))

from reportlab.lib.fonts import addMapping

addMapping('BlairMdITC_TT_Medium', 0, 0, 'BlairMdITC_TT_Medium')  
#addMapping('BlairMdITC_TT_Medium-Bold', 1, 0, 'BlairMdITC_TT_Medium')