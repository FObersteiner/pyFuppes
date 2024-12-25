# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

import numpy as np
from pyfuppes import misc


class TestTimecorr(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # to run before all tests
        pass

    @classmethod
    def tearDownClass(cls):
        # to run after all tests
        pass

    def setUp(self):
        # to run before each test
        pass

    def tearDown(self):
        # to run after each test
        pass

    def test_listelement(self):
        a = [1, 2, 3]
        b = misc.list_change_elem_index(a, 3, 0)
        self.assertListEqual(b, [3, 1, 2])
        self.assertListEqual(a, [1, 2, 3])
        with self.assertRaises(IndexError):
            _ = misc.list_change_elem_index(a, 3, 5)

    def test_pathcleaner(self):
        p = "$HOME"
        clean_p = misc.clean_path(p)
        self.assertEqual(clean_p.as_posix(), Path().home().as_posix())
        p = "~"
        clean_p = misc.clean_path(p)
        self.assertEqual(clean_p.as_posix(), Path().home().as_posix())
        p = "$HOME/a_directory"
        clean_p = misc.clean_path(p)
        self.assertEqual(clean_p.as_posix(), (Path().home() / "a_directory").as_posix())

    def test_findfirst(self):
        arr = np.arange(10)
        elem = misc.find_fist_elem(arr, 4, lambda x, y: x > y)
        self.assertEqual(5, elem)
        lst = list(range(10))
        elem = misc.find_fist_elem(lst, 4, lambda x, y: x > y)
        self.assertEqual(5, elem)


if __name__ == "__main__":
    unittest.main()
