from dataclasses import dataclass
from .connection_manager import _ConnectionManager
import os
import json


def get_default_globalite() -> "_Globalite":
    return _Globalite("settings.db", "globals")


@dataclass
class _Globalite:

    __protected_names = [
        "keys",
        "flush_database",
        "_globalite_variables"
    ]

    def __init__(self, db_file: str, table_name: str):
        self._globalite_variables = {
            "db_file": db_file,
            "table_name": table_name,
            "connection_manager": _ConnectionManager(db_file),
        }

        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self) -> None:
        with self.__get_connection() as (conn, cursor):
            if self._has_table(cursor):
                return

            query = f"CREATE TABLE IF NOT EXISTS {self._globalite_variables.get('table_name')} (key TEXT, value TEXT, type TEXT, PRIMARY KEY (key))"

            cursor.execute(query)
            conn.commit()

    def _has_table(self, cursor) -> bool:
        query = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?"
        cursor.execute(query, (self._globalite_variables.get('table_name'),))

        return cursor.fetchone()[0] > 0

    def __get_connection(self) -> "_ConnectionManager":
        # return self._gl_connection_manager
        return self._globalite_variables.get("connection_manager")

    def __setattr__(self, __name: str, __value) -> None:
        if __name == "_globalite_variables" or __name in self._globalite_variables.keys():
            super().__setattr__(__name, __value)
        elif __name in _Globalite.__protected_names:
            raise NameError("Attribute name can not be the same as an existing function")
        else:
            with self.__get_connection() as (conn, cursor):
                query = f"INSERT OR REPLACE INTO {self._globalite_variables.get('table_name')} (key, value, type) VALUES(?, ?, ?)"
                if type(__value) is dict:
                    cursor.execute(query, (__name, json.dumps(__value), str(type(__value).__name__)))
                else:
                    cursor.execute(query, (__name, __value, str(type(__value).__name__)))
                conn.commit()

    def __getattr__(self, __name: str) -> None:
        if __name == "_globalite_variables" or __name in self._globalite_variables.keys():
            return super().__getattr__(__name)
        with self.__get_connection() as (_, cursor):
            query = f"SELECT value, type FROM {self._globalite_variables.get('table_name')} WHERE key = ?"
            cursor.execute(query, (__name,))
            result = cursor.fetchone()
            if result is None:
                raise AttributeError(f"'{self.__class__.__name__}' has no object '{__name}'")
            _type = result[1]
            if _type == "dict":
                return json.loads(result[0])
            if _type == "int":
                return int(result[0])
            if _type == "bool":
                return bool(int(result[0]))
            if _type == "float":
                return float(result[0])
            if _type == "str" or _type =="NoneType":
                return result[0]
            raise ValueError(f"Unsupported value type '{_type}' for key '{__name}' value '{result[0]}'")

    def __delattr__(self, __name: str) -> None:
        if __name in self._globalite_variables.keys():
            super().__delattr__(__name)
        else:
            with self.__get_connection() as (conn, cursor):
                query = f"DELETE FROM {self._globalite_variables.get('table_name')} WHERE key = ?"
                cursor.execute(query, (__name,))
                conn.commit()

    def keys(self) -> set:
        keys: set[str] = set()
        with self.__get_connection() as (_, cursor):
            query = f"SELECT key FROM {self._globalite_variables.get('table_name')}"
            cursor.execute(query)
            for item in cursor.fetchall():
                keys.add(item[0])
        return keys

    def flush_database(self) -> None:
        '''
            Will flush the database file, meaning it will do the fsync system call
            that makes sure the database file is written to disk.

            OBS use with caution and only when a value is at risk of being forgotten by
            a soon thereafter power outage. The operation is more expensive, performance-wise,
            than normal save.

            The OS does these for the full system regularly so it is only needed in rare occasions.

            https://www.tutorialspoint.com/python/os_fsync.htm
            https://www.sqlite.org/atomiccommit.html (9.2 Incomplete Disk Flushes)
        '''
        with open(self._globalite_variables.get('db_file')) as f:
            os.fsync(f)
