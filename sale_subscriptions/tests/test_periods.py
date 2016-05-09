# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Didotech SRL (info at didotech.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# warranty and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.tests.common import TransactionCase
import unittest2


class Order(object):
    # %Y-%m-%d
    order_start_date = ''
    # Duration in days
    order_duration = 0
    # Duration in days
    order_invoice_duration = 0
    # '1' or '31'
    subscription_invoice_day = '1'


class TestPeriods(TransactionCase):
    def setUp(self):
        super(TestPeriods, self).setUp()
        self.order_obj = self.registry('sale.order')

    def test_invoice_dates(self):
        order = Order()
        order.order_start_date = '2016-01-02'
        # order.order_duration = 365
        order.order_invoice_duration = 90
        order.subscription_invoice_day = 1
        invoice_dates = self.order_obj.get_invoice_dates(self.cr, self.uid, order, 365, 90, context={})
        self.assertEqual(invoice_dates[0]['period'], 'Gennaio 2016 - Marzo 2016')

if __name__ == '__main__':
    unittest2.main()
