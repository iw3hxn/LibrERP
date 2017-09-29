# -*- coding: utf-8 -*-
# Copyright 2017 - Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>
#                  Associazione Odoo Italia <http://www.odoo-italia.org>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
{
    "name": "Base xml Agenzia delle Entrate",
    "version": "7.0.0.1.0",
    "category": "Localization/Italy",
    "summary": "Codice con le definizioni dei file xml Agenzia delle Entrate",
    "author": "SHS-AV s.r.l.,"
              " Odoo Italia Associazione",
    "maintainer": "Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>",
    "description": """(en)

Italian Localization - Definition for xml files
===============================================

This module has no any specific function for End-user. It is base for modules
generate xml file like FatturaPA o VAT settlement.

This module requires PyXB 1.2.4
http://pyxb.sourceforge.net/


(it)

Localizzazione italiana - Definizioni per file xml
==================================================

Questo modulo non ha funzioni specifice per l'utente finale. Serve come base
per i moduli che generano file xml in formato stabilito dall'Agenzia delle
Entrate, come FatturaPA o Liquidazione IVA elettronica.

Attenzione! Questo modulo è incompatibile con i moduli l10n_it_fatturapa di OCA
versioni [7-11].0.2.0.0
Lo schema di definizione dei file xml dell'Agenzia delle Entrate, pubblicato
con urn:www.agenziaentrate.gov.it:specificheTecniche è base per tutti i file
xml; come conseguenza nasce un conflitto tra moduli diversi con lo stesso
schema di riferimento dell'Agenzia delle Entrate con l'errore:
*name CryptoBinary used for multiple values in typeBinding*

Tutti i moduli che generano file xml per l'Agenzia delle Entrate *devono*
dipendere da questo modulo.
Per maggiori informazioni visitare il sito www.odoo-italia.org o contattare
l'autore.

Schemi
------

Il modulo rende disponibili i seguenti schemi:

* Liquidazione IVA elettronica versione 1.0
* Comunicazione clienti e fornitori (spesometro 2017) versione 2.0
* FatturaPA versione 1.2
""",
    "license": "AGPL-3",
    "depends": [],
    "data": [],
    'installable': True,
    "external_dependencies": {
        "python": ["pyxb"],
    }
}
