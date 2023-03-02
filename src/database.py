import sqlite3
from enum import Enum
from pathlib import Path
from typing import Tuple, List, Union, Optional, Mapping, Any

from pydantic import BaseModel


SQL_KEY_STRING = [
    'select', 'where', 'order', 'limit',
    'offset', 'delete', 'pragma', 'alter'
]


class SqliteType(Enum):
    INTEGER = "INTEGER"
    PRIMARY = "PRIMARY KEY"
    REAL = "REAL"
    TEXT = "TEXT"
    BLOB = "BLOB"
    NULL = "NULL"


class Sql(str):
    def __init__(self, base_sql: str = ''):
        assert self._check_if_sql(base_sql)
        self.__split_sql: list = self.split_sql()
        super().__init__(base_sql)

    @staticmethod
    def _check_if_sql(sql: str):
        if any(_[0].startswith(_[1]) for _ in zip([sql.split()[0].lower()] * len(SQL_KEY_STRING), SQL_KEY_STRING)):
            return True
        return False

    def split_sql(self) -> list:
        split_ = self.split()
        index_list = [
            index for index, s in enumerate(split_) if s.lower() in SQL_KEY_STRING
        ]
        return [
            split_[:index_] if pos == 0 else split_[index_ - 1:index_]
            for pos, index_ in enumerate(index_list)
        ]

    def join_sql(self, other: str):
        self.__split_sql.append(other)


class Database:
    def __init__(self, db: Union[str, Path]):
        if isinstance(db, Path):
            db = str(db.absolute())
        self._conn = sqlite3.connect(db)
        self.commit = self._conn.commit

    def __getattr__(self, item):
        return Table(item, self)

    def __getitem__(self, item):
        return Table(item, self)

    def _get_cursor(self):
        return self._conn.cursor()

    def list_tables(self) -> list:
        cursor_ = self.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return list(cursor_.fetchall())

    def execute(self, sql: str, params: Union[Tuple[Union[str, bytes, bytearray, memoryview, int, float]], None] = None):
        cursor = self._get_cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        self._conn.commit()
        return cursor

    def create_table(self, name: str, columns: List[Tuple[str, SqliteType, Optional[bool]]],
                     gen_id: Optional[bool] = True):
        if not all(isinstance(datatype, SqliteType) for col, datatype in columns):
            raise TypeError("Datatype must be a SqliteType")
        if gen_id:
            columns = [('ID', SqliteType), *columns]
        formatted_table_schema = ', '.join(
            f'{col[0]} {col[1].value}' if len(col) == 2 else f'{col[0]} {col[1].value} NOT NULL' for col in columns
        )
        create_table_sql = f'create table if not exists {name} ({formatted_table_schema})'
        self.execute(sql=create_table_sql)


class Table:
    def __init__(self, name: str, __database: Database):
        self._name = name
        self._database = __database

        self.execute = self._database.execute
        self.commit = self._database.commit

    @staticmethod
    def _check_column_def(columns: List[Tuple[str, SqliteType, Optional[bool]]]) -> bool:
        if all(isinstance(col_, tuple) for col_ in columns):
            return True
        return False

    def exists(self):
        _result = self.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self._name}';"
        ).fetchall()
        if _result:
            return True
        return False

    def get_schema(self):
        _schema_info = self.execute(f'pragma table_info({self._name});').fetchall()
        return ', '.join(f'{si_[1]} {si_[2]}{" NOT NULL" if si_[3] else ""}' for si_ in _schema_info)

    def drop(self):
        self.execute(f'drop table if exists {self._name}')

    def delete(self, __filter: Mapping[str, Any], maximum: int = None, auto_commit: bool = True):
        delete_sql = f'delete from {self._name}'
        if __filter:
            delete_sql += ' where ' + \
                          ' and '.join(f'{k} == ?' for k in __filter.keys())
        if maximum:
            delete_sql += f' limit {maximum}'
        cursor = self.execute(delete_sql)

    def find(self, __filter: Mapping[str, Any], maximum: int = None):
        find_sql = f'select * from {self._name} where ' + \
                   ' and '.join(f'{k} == ?' for k in __filter.keys())
        if maximum:
            find_sql += f' limit {maximum}'
        return self.execute(find_sql, params=tuple(__filter.values())).fetchall()

    def find_one(self, __filter: Mapping[str, Any]):
        find_sql = f'select * from {self._name} where ' + \
                   ' and '.join(f'{k} == ?' for k in __filter.keys()) + ' limit 1'
        return self.execute(find_sql, params=tuple(__filter.values())).fetchone()

    def insert(self, __obj: Mapping[str, Any], auto_commit: bool = True):
        insert_sql = f'insert into {self._name} ({", ".join(__obj.keys())}) values ({", ".join(__obj.values())})'
        cursor_ = self.execute(insert_sql)
        if auto_commit:
            self.commit()
        return cursor_.rowcount

    def update(self, __filter: Mapping[str, Any], __updates: Mapping[str, Any], auto_commit: bool = True):
        where_sql_snippet = ' and '.join(f'{k} == ?' for k in __filter.keys())
        set_sql_snippet = ', '.join(f'{k} = ?' for k in __updates.keys())
        update_sql = f'update {self._name} set {set_sql_snippet} where {where_sql_snippet}'
        cursor_ = self.execute(update_sql)
        if auto_commit:
            self.commit()
        return cursor_.rowcount
