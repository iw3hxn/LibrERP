# -*- coding: utf-8 -*-
# © 2017-2018 Didotech srl (www.didotech.com)
"""
Disable openerp related imports in utils.py before running tests
"""

from utils import Utils


def test_conversion():
    to_str = Utils.toStr

    values = {
        '234': '234',
        '2,23': '2.23',
        '2.234,78': '2234.78',
        '2.33': '2.33',
        '3,678.98': '3678.98',
        '0.98': '0.98',
        '0,98': '0.98',
        '0,085': '0.085',
        '00,085': '00,085',
        '00.085': '00.085',
        '02.085': '02.085',
        '02,085': '02,085',
        '.': '.',
        ',': ',',
        'L00df': 'L00df',
        u'€ 4.072,00': '4072.0'
    }

    for value, result in values.items():
        assert to_str(value) == result, u"{} is not {}".format(value, result)


if __name__ == '__main__':
    test_conversion()
