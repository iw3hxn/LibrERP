# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2016 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common
from openerp.addons.export_teamsystem.wizard.export_primanota import get_phone_number


class TestPhoneMethod(common.TransactionCase):
    def test_number(self):
        phone = get_phone_number('0495841300', '49')
        self.assertEqual(phone['prefix'], '049')
        self.assertEqual(phone['number'], '5841300')

    def test_number_without_space(self):
        phone = get_phone_number('0495841300', False)
        self.assertEqual(phone['prefix'], '0495')
        self.assertEqual(phone['number'], '841300')

    def test_number_without_space_wrong_prefix(self):
        phone = get_phone_number('3475841300', '49')
        self.assertEqual(phone['prefix'], '3475')
        self.assertEqual(phone['number'], '841300')

    def test_number_with_space_wrong_prefix(self):
        phone = get_phone_number('347 1234567', '49')
        self.assertEqual(phone['prefix'], '347')
        self.assertEqual(phone['number'], '1234567')

    def test_number_with_space(self):
        phone = get_phone_number('049 5841300', False)
        self.assertEqual(phone['prefix'], '049')
        self.assertEqual(phone['number'], '5841300')

    def test_number_with_spaces(self):
        phone = get_phone_number('049 58 41 300', '49')
        self.assertEqual(phone['prefix'], '049')
        self.assertEqual(phone['number'], '5841300')

    def test_cell_number_with_space_no_prefix(self):
        phone = get_phone_number('347 1234567', False)
        self.assertEqual(phone['prefix'], '347')
        self.assertEqual(phone['number'], '1234567')
