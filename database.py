import sqlite3
from enum import Enum
from pathlib import Path
from typing import Tuple, List, Union, Optional, get_type_hints


class SqliteType(Enum): 
    INTEGER = "INTEGER"
    PRIMARY = "PRIMARY KEY"
    REAL = "REAL"
    TEXT = "TEXT"
    BLOB = "BLOB"
    NULL = "NULL"


class TableBase:
    def _get_typing_hints(self):
        return


class Database:
    def __init__(self, db: Union[str, Path]):
        self._conn = sqlite3.connect(str(db))

    def _get_cursor(self):
        return self._conn.cursor()

    def _chk_column_def(self, columns: List[Tuple[str, SqliteType, Optional[bool]]]) -> bool:
        if all(isinstance(col_, tuple) and len(col_) >= 2 and len() for col_ in columns)
            return True
        return False



    def list_tables(self) -> list:
        cursor_ = self.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return list(cursor_.fetchall())

    def execute(self, sql: str, params: Tuple = None):
        cursor = self._get_cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        self._conn.commit()
        return cursor

    def create_table(self, name: str, columns: List[Tuple[str, SqliteType, Optional[bool]]], gen_id: Optional[bool] = True):
        if not all(isinstance(datatype, SqliteType) for col, datatype in columns):
            raise TypeError("Datatype must be a SqliteType")
        if gen_id:
            columns = [('ID', SqliteType)]
        formatted_table_schema = ', '.join(
            f'{col[0]} {col[1].value}' if len(col) == 2 else f'{col[0]} {col[1].value} NOT NULL' for col in columns
        )
        table_sql = f'CREATE TABLE IF NOT EXISTS {name} ({formatted_table_schema})'


class Table:
    def __init__(self, name: str, columns: List[Tuple[str, SqliteType]], db: Database):
        self.name = name
        self.columns = columns