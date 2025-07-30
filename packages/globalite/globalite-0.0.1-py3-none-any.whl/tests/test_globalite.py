from __future__ import annotations
import os
import unittest
from tests import TempDirFixture
from unittest import TestCase

from tests.context import globalite

_test_db = "test.db"
_test_table = "globals"

class TestGlobalite(TempDirFixture, TestCase):

    def setUp(self):
        super().setUp()

        self.globalite = globalite._Globalite(_test_db, _test_table)
        self.globalite.test_int = 20
        self.globalite.test_float = 2.1
        self.globalite.test_string = "test string"
        self.globalite.test_bool = False
        self.globalite.test_dict = {
            "valueInt": 5,
            "valueFloat": 3.2,
            "valueStr": "Hello World",
            "valueBool": True,
            "valueDict": {"valueDictInt": 2},
            "valueNone": None,
        }
        self.globalite.test_nonetype = None

    def tearDown(self):
        if os.path.isfile(_test_db):
            os.remove(_test_db)

        super().tearDown()

    def test_read_int(self):
        _var_int = self.globalite.test_int
        self.assertEqual(type(_var_int), int)
        self.assertEqual(_var_int, 20)

    def test_read_float(self):
        _var_float = self.globalite.test_float
        self.assertEqual(type(_var_float), float)
        self.assertEqual(_var_float, 2.1)

    def test_read_str(self):
        _var_string = self.globalite.test_string
        self.assertEqual(type(_var_string), str)
        self.assertEqual(_var_string, "test string")

    def test_read_bool(self):
        _var_bool = self.globalite.test_bool
        self.assertEqual(type(_var_bool), bool)
        self.assertEqual(_var_bool, False)

    def test_read_dict(self):
        _var_test_dict: dict = self.globalite.test_dict
        self.assertEqual(type(_var_test_dict), dict)

        _var_int: int = _var_test_dict["valueInt"]
        self.assertEqual(type(_var_int), int)
        self.assertEqual(_var_int, 5)

        _var_float: float = _var_test_dict["valueFloat"]
        self.assertEqual(type(_var_float), float)
        self.assertEqual(_var_float, 3.2)

        _var_str: str = _var_test_dict["valueStr"]
        self.assertEqual(type(_var_str), str)
        self.assertEqual(_var_str, "Hello World")

        _var_bool: bool = _var_test_dict["valueBool"]
        self.assertEqual(type(_var_bool), bool)
        self.assertTrue(_var_bool)

        _var_dict: dict = _var_test_dict["valueDict"]
        self.assertEqual(type(_var_dict), dict)
        self.assertEqual(_var_dict, {"valueDictInt": 2})

        _var_none: None = _var_test_dict["valueNone"]
        self.assertIsInstance(_var_none, type(None))
        self.assertIsNone(_var_none)

    def test_read_nonetype(self):
        _var_none: None = self.globalite.test_nonetype
        self.assertIsInstance(_var_none, type(None))
        self.assertIsNone(_var_none)

    def test_write_int(self):
        self.globalite._var_int = 1
        self.assertEqual(type(self.globalite._var_int), int)
        self.assertEqual(self.globalite._var_int, 1)

    def test_write_float(self):
        self.globalite._var_float = 2.1
        self.assertEqual(type(self.globalite._var_float), float)
        self.assertEqual(self.globalite._var_float, 2.1)

    def test_write_bool(self):
        self.globalite._var_bool = False
        self.assertEqual(type(self.globalite._var_bool), bool)
        self.assertFalse(self.globalite._var_bool)

    def test_write_str(self):
        self.globalite._var_str = "World Hello"
        self.assertEqual(type(self.globalite._var_str), str)
        self.assertEqual(self.globalite._var_str, "World Hello")

    def test_write_dict(self):
        self.globalite._var_dict = {"varStr": "dict String", "varInt": 6}
        self.assertEqual(type(self.globalite._var_dict), dict)
        self.assertEqual(self.globalite._var_dict, {"varStr": "dict String", "varInt": 6})

    @unittest.skip("Update a dict does not work as intended at this moment, because globalite generates a new object every getattribute")
    def test_update_dict(self):
        _temp_dict = self.globalite._var_dict = {"varStr": "dict String", "varInt": 6}
        self.assertEqual(_temp_dict, self.globalite._var_dict)
        self.assertIs(_temp_dict, self.globalite._var_dict)


    def test_write_nonetype(self):
        '''
            Making sure the __setattr__ has been implemented correctly for nonetypes,
            by writting a variable and reading it back.
            Also ensuring that 'None' is not just a default return for variables that has not been set.
        '''
        with self.assertRaises(AttributeError):
            self.globalite.temp_var
        self.globalite.temp_var = None
        self.assertEqual(self.globalite.temp_var, None)

    def test_delete(self):
        self.globalite.test_int
        del self.globalite.test_int
        self.assertFalse(hasattr(self.globalite, "test_int"))
        with self.assertRaises(AttributeError):
            self.globalite.test_int

    @unittest.skip("Deletion in dict does not work as intended at this moment")
    def test_delete_in_dict(self):
        self.globalite.test_dict["valueInt"]
        del self.globalite.test_dict["valueInt"]

        self.assertEqual(self.globalite.test_dict, self.globalite.test_dict)
        self.assertIs(self.globalite.test_dict, self.globalite.test_dict)

        with self.assertRaises(AttributeError):
            self.globalite.test_dict["valueInt"]

    def test_read_not_initiated_variable(self):
        with self.assertRaises(AttributeError):
            self.globalite._not_init_variable

    def test_get_key_set(self):
        _amount_of_keys = 6
        _expected_keys = ["test_int", "test_float", "test_string", "test_bool", "test_dict", "test_nonetype"]
        _keys: set = self.globalite.keys()
        for key in _keys:
            self.assertIn(key, _expected_keys)

        self.assertEqual(_amount_of_keys, len(_keys))

    def test_flush_database(self):
        '''
            Test if flush_database crashes.

            This method is closely hardware related and needs to be tested based on OS and hardware.
            Therefore this test just ensures that the method can be called and doesn't crash.

        '''
        self.globalite.flush_database()

    def test_method_names(self):
        '''
            Test if the names used for the methods in Globalite
            is protected properly
        '''
        # Globalite.keys
        _temp_func_type = type(self.globalite.keys)
        with self.assertRaises(NameError):
            self.globalite.keys = "string for keys"

        self.assertEqual(type(self.globalite.keys), _temp_func_type)

        # Globalite.flush_database
        _temp_func_type = type(self.globalite.flush_database)
        with self.assertRaises(NameError):
            self.globalite.flush_database = "string for flush database"

        self.assertEqual(type(self.globalite.flush_database), _temp_func_type)


class TestGlobaliteInitialization(TestCase):
    pass

class TestGlobalsPersistency(TestCase):
    pass

if __name__ == "__main__":
    unittest.main()