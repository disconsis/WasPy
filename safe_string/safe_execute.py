from forbiddenfruit import curse
import sqlite3
import psycopg2
import mysql.connector
from functools import wraps

import sql

__completed = False


def wrap(class_, unsafe_func):
    @wraps(unsafe_func)
    def safe_func(self, query, *args, **kwargs):
        # print(f'DEBUG: calling {class_.__module__}.{unsafe_func.__name__}')
        if sql.sqli(query):
            print("[!] SQLi detected in {}".format(class_.__module__))
            print(f"query: {query!r}")
            # FIXME: replace with the module's error type
            raise RuntimeError("sqli detected")

        return unsafe_func(self, query, *args, **kwargs)

    return safe_func


if not __completed:
    unsafe_execute_classes = [
        sqlite3.Connection,
        sqlite3.Cursor,
        psycopg2.extensions.cursor,
        mysql.connector.cursor_cext.CMySQLCursor,
    ]

    for class_ in unsafe_execute_classes:
        for func_name in ("execute", "executemany"):
            try:
                unsafe_func = getattr(class_, func_name)
            except AttributeError:
                pass
            else:
                safe_func = wrap(class_, unsafe_func)
                curse(class_, func_name, safe_func)

    __completed = True
