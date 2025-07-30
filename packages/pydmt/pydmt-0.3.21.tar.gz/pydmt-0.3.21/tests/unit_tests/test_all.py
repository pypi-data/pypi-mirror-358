"""
test_all.py
"""

import unittest

import shutil

import os

from pydmt.api.fail import Fail
from pydmt.core.pydmt import PyDMT, BuildProcessStats
from pydmt.api.copy import Copy
from pydmt.core.tempdir import tempdir


class TestAll(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # import pylogconf.core
        # pylogconf.core.setup()
        pass

    def test00CreatePyDMT(self):
        PyDMT()

    def test01NullBuild(self):
        p = PyDMT()
        p.build_all()

    def test02ReturnType(self):
        p = PyDMT()
        stats = p.build_all()
        self.assertIsInstance(stats, BuildProcessStats, "must be BuildProcessStats")

    @staticmethod
    def get_std_test():
        shutil.copy("/etc/passwd", "passwd")
        p = PyDMT()
        b = Copy("passwd", "copy_of_passwd")
        p.add_builder(b)
        return p.build_all()

    def test03SimpleCopy(self):
        with tempdir():
            stats = self.get_std_test()
            self.assertEqual(stats.get_builder_ok(), 1)
            self.assertEqual(stats.get_copy_missing(), 0)

    def test04Incremental(self):
        with tempdir():
            stats = self.get_std_test()
            self.assertEqual(stats.get_builder_ok(), 1)
            self.assertEqual(stats.get_copy_missing(), 0)
            self.assertEqual(stats.get_nop(), 0)

    def test05CopyAfterRemove(self):
        with tempdir():
            shutil.copy("/etc/passwd", "passwd")
            p = PyDMT()
            b = Copy("passwd", "copy_of_passwd")
            p.add_builder(b)
            p.build_all()
            os.unlink("copy_of_passwd")
            stats = p.build_all()
            self.assertEqual(stats.get_builder_ok(), 0)
            self.assertEqual(stats.get_builder_fail(), 0)
            self.assertEqual(stats.get_nop(), 0)
            self.assertEqual(stats.get_copy_missing(), 1)

    def test06Fail(self):
        with tempdir():
            shutil.copy("/etc/passwd", "passwd")
            p = PyDMT()
            b = Fail("passwd", "copy_of_passwd")
            p.add_builder(b)
            stats = p.build_all()
            self.assertEqual(stats.get_builder_ok(), 0)
            self.assertEqual(stats.get_builder_fail(), 1)
            self.assertEqual(stats.get_copy_missing(), 0)
            self.assertEqual(stats.get_nop(), 0)
