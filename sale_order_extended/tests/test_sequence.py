#!/usr/bin/env python

import imp
import os
import unittest

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

utility = imp.load_source('utility', os.path.join(ROOT_PATH, 'models/utility.py'))
set_sequence = utility.set_sequence


class Sequence(unittest.TestCase):
    def test_sequence(self):
        tests = [
            {
                'lines': [
                    (4, False, False),
                    (0, False, {'sequence': 20}),
                    (0, False, {'sequence': 20}),
                    (0, False, {'sequence': 20})
                ],
                'reply': (False, 20, 30, 40)
            },
            {
                'lines': [
                    (4, False, False),
                    (0, False, {'sequence': 15}),
                    (4, False, False),
                    (0, False, {'sequence': 30}),
                    (0, False, {'sequence': 30}),
                    (0, False, {'sequence': 30})
                ],
                'reply': (False, 15, False, 30, 40, 50)
            },
            {
                'lines': [
                    (0, False, {'sequence': 10}),
                    (0, False, {'sequence': 20}),
                    (0, False, {'sequence': 30})
                ],
                'reply': (10, 20, 30)
            },
            {
                'lines': [
                    (0, False, {'sequence': 10}),
                    (0, False, {'sequence': 12}),
                    (0, False, {'sequence': 16})
                ],
                'reply': (10, 20, 30)
            },
            {
                'lines': [
                    (0, False, {'sequence': 10}),
                    (0, False, {'sequence': 10}),
                    (0, False, {'sequence': 10})
                ],
                'reply': (10, 20, 30)
            },
            {
                'lines': [
                    (0, False, {'sequence': 10}),
                    (0, False, {'sequence': 10}),
                    (0, False, {'sequence': 12})
                ],
                'reply': (10, 20, 30)
            },
            {
                'lines': [
                    (0, False, {'sequence': 5}),
                    (0, False, {'sequence': 10}),
                    (0, False, {'sequence': 12})
                ],
                'reply': (10, 20, 30)
            },
            {
                'lines': [
                    (4, False, False),
                    (0, False, {'sequence': 12}),
                    (0, False, {'sequence': 14}),
                    (0, False, {'sequence': 14}),
                    (4, False, False),
                    (4, False, False)
                ],
                'reply': (False, 12, 14, 16, False, False)
            },
            {
                'lines': [
                    (4, False, False),
                    (0, False, {'sequence': 18}),
                    (0, False, {'sequence': 18}),
                    (0, False, {'sequence': 18}),
                ],
                'reply': (False, 20, 30, 40)
            },
            {
                'lines': [
                    (4, False, False),
                    (4, False, False),
                    (4, False, False),
                    (0, False, {'sequence': 15})
                ],
                'reply': (False, False, False, 40)
            },
        ]

        for test_set in tests:
            lines = set_sequence(test_set['lines'])
            for count, line in enumerate(lines):
                if line[2]:
                    self.assertEqual(line[2]['sequence'], test_set['reply'][count])


if __name__ == '__main__':
    unittest.main()
