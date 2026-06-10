# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2025 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)

# Journals that count as non-conformity (no keyword check on picking note)
_NC_ONLY_NAMES = [
    'C/Repair',
    'C/repair under warranty',
    'C/replacement under warranty',
    'Made for Replacement',
    'C/Riparazione',
    'C/riparazione in garanzia',
    'C/sostituzione in garanzia',
    'Reso per Sostituzione',
]

# Journals that count as non-conformity only when the picking note
# contains 'RMA' or 'Reso' (case-insensitive)
_NC_CHECK_NOTE_NAMES = [
    'Return',
    'Return to Vendor',
    'Reso',
    'Reso a Fornitore',
]


class StockJournalInherit(orm.Model):
    _inherit = 'stock.journal'

    _columns = {
        'nonconformity': fields.boolean(
            'Non Conformità',
            help="I picking con questo giornale contano come non conformità fornitore",
        ),
        'nonconformity_check_note': fields.boolean(
            'NC solo se note RMA/Reso',
            help="Conta come NC solo se le note del picking contengono 'RMA' o 'Reso'",
        ),
    }

    def init_nonconformity_flags(self, cr, uid, context=None):
        """
        Flag known standard journal names with the appropriate nonconformity
        booleans.  Uses exact case-insensitive match to avoid substring
        collisions (e.g. "Reso" must not match "Reso per Sostituzione" which
        belongs to the nc-only list).
        """
        # Process nc-only list first so that "Reso per Sostituzione" gets
        # flagged before the check-note list loop runs and cannot accidentally
        # receive check_note=True.
        all_ids = self.search(cr, uid, [], context=context)
        all_journals = self.read(cr, uid, all_ids, ['id', 'name'], context=context)

        nc_only_lower = [n.lower() for n in _NC_ONLY_NAMES]
        nc_check_lower = [n.lower() for n in _NC_CHECK_NOTE_NAMES]

        for journal in all_journals:
            jname_lower = (journal['name'] or '').lower()
            if jname_lower in nc_only_lower:
                self.write(cr, uid, [journal['id']], {
                    'nonconformity': True,
                    'nonconformity_check_note': False,
                }, context=context)
            elif jname_lower in nc_check_lower:
                self.write(cr, uid, [journal['id']], {
                    'nonconformity': True,
                    'nonconformity_check_note': True,
                }, context=context)

        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
