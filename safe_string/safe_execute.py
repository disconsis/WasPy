from forbiddenfruit import curse
import sqlite3
import psycopg2
import mysql.connector
from functools import wraps

import sql

__completed = False


def wrap(class_, unsafe_func, error_class):
    @wraps(unsafe_func)
    def safe_func(self, query, *args, **kwargs):
        # print(f'DEBUG: calling {class_.__module__}.{unsafe_func.__name__}')
        if sql.sqli(query):
            print("[!] SQLi detected in {}".format(class_.__module__))
            print(f"query: {query!r}")
            raise error_class("sqli detected")

        return unsafe_func(self, query, *args, **kwargs)

    return safe_func


if not __completed:
    unsafe_execute_classes = [
        (sqlite3.Connection, sqlite3.Error),
        (sqlite3.Cursor, sqlite3.Error),
        (psycopg2.extensions.cursor, psycopg2.OperationalError),
        (mysql.connector.cursor_cext.CMySQLCursor, mysql.connector.Error),
    ]

    for class_, error_class in unsafe_execute_classes:
        for func_name in ("execute", "executemany"):
            try:
                unsafe_func = getattr(class_, func_name)
            except AttributeError:
                pass
            else:
                safe_func = wrap(class_, unsafe_func, error_class)
                curse(class_, func_name, safe_func)

    __completed = True
