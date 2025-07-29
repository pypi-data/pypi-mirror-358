import unittest

from pyresult.result import Err, Ok, Result


class TestResult(unittest.TestCase):
    def test_is_ok(self):
        self.assertTrue(Ok(1).is_ok)
        self.assertFalse(Err(1).is_ok)

    def test_is_err(self):
        self.assertTrue(Err(1).is_err)
        self.assertFalse(Ok(1).is_err)

    def test_ok_and_err(self):
        self.assertEqual(Ok(1).ok(), 1)
        self.assertIsNone(Err(1).ok())
        self.assertEqual(Err(1).err(), 1)
        self.assertIsNone(Ok(1).err())

    def test_contains(self):
        self.assertTrue(Ok(1).contains(1))
        self.assertFalse(Ok(1).contains(2))
        self.assertFalse(Err(1).contains(1))

    def test_contains_err(self):
        self.assertTrue(Err(1).contains_err(1))
        self.assertFalse(Err(1).contains_err(2))
        self.assertFalse(Ok(1).contains_err(1))

    def test_map(self):
        self.assertEqual(Ok(1).map(lambda x: x + 1), Ok(2))
        self.assertEqual(Err(1).map(lambda x: x + 1), Err(1))

    def test_map_err(self):
        self.assertEqual(Ok(1).map_err(lambda x: x + 1), Ok(1))
        self.assertEqual(Err(1).map_err(lambda x: x + 1), Err(2))

    def test_and_then(self):
        self.assertEqual(Ok(1).and_then(lambda x: Ok(x + 1)), Ok(2))
        self.assertEqual(Ok(1).and_then(lambda x: Err(x + 1)), Err(2))
        self.assertEqual(Err(1).and_then(lambda x: Ok(x + 1)), Err(1))

    def test_or_else(self):
        self.assertEqual(Ok(1).or_else(lambda x: Ok(x + 1)), Ok(1))
        self.assertEqual(Err(1).or_else(lambda x: Ok(x + 1)), Ok(2))
        self.assertEqual(Err(1).or_else(lambda x: Err(x + 1)), Err(2))

    def test_unwrap(self):
        self.assertEqual(Ok(1).unwrap(), 1)
        with self.assertRaises(Exception):
            Err(1).unwrap()

    def test_unwrap_err(self):
        self.assertEqual(Err(1).unwrap_err(), 1)
        with self.assertRaises(Exception):
            Ok(1).unwrap_err()

    def test_unwrap_or(self):
        self.assertEqual(Ok(1).unwrap_or(2), 1)
        self.assertEqual(Err(1).unwrap_or(2), 2)

    def test_unwrap_or_else(self):
        self.assertEqual(Ok(1).unwrap_or_else(lambda x: x + 1), 1)
        self.assertEqual(Err(1).unwrap_or_else(lambda x: x + 1), 2)
