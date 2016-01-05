# -*- coding: utf-8 -*-
"""
Test different parts of Moliana.

@author: jmoeckel
"""

import os
import unittest

os.chdir('../example')
import examples

class TestMolianaMethods(unittest.TestCase):

    def setUp(self):
        pass

    def _readReport(self, rep):
        with open('..//tests//reports//{}.html'.format(rep)) as file_validated:
            validated = file_validated.read().splitlines();

        with open('reports//{}.html'.format(rep)) as file_new:
            new = file_new.read().splitlines();

        return validated, new

    def test_example1(self):
        self.assertIs(examples.example1(),True)

        validated, new = self._readReport('example1')
        self.assertListEqual(new,validated)

    def test_example2(self):
        self.assertIs(examples.example2(),True)

        validated, new = self._readReport('example2')
        self.assertListEqual(new,validated)

    def test_example3(self):
        self.assertIs(examples.example3(),True)

        validated, new = self._readReport('example3')
        self.assertListEqual(new,validated)

    def test_example4(self):
        self.assertIs(examples.example4(),True)

        validated1, new1 = self._readReport('example41')
        self.assertListEqual(new1,validated1)

        validated2, new2 = self._readReport('example42')
        self.assertListEqual(new2,validated2)

    def test_example5(self):
        self.assertIs(examples.example5(),True)

        validated, new = self._readReport('example5')
        self.assertListEqual(new,validated)

    def test_example6(self):
        self.assertIs(examples.example6(),True)

        validated1, new1 = self._readReport('example6')
        self.assertListEqual(new1,validated1)

        validated2, new2 = self._readReport('example6_compare')
        self.assertListEqual(new2,validated2)

    def test_example7(self):
        self.assertIs(examples.example7(),True)

        validated, new = self._readReport('example7')
        self.assertListEqual(new,validated)

if __name__ == '__main__':
    unittest.main(verbosity=2)
