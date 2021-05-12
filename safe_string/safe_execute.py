from forbiddenfruit import curse
import sqlite3
import psycopg2
import mysql.connector
from functools import wraps

import sql

__completed = False


if not __completed:
    unsafe_execute_classes = [
        sqlite3.Connection,
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
                @wraps(unsafe_func)
                def safe_func(self, query, *args, **kwargs):
                    if sql.sqli(query):
                        print("[!] SQLi detected in {}".format(class_.__module__))
                        print(f"query: {query!r}")
                        return

                    return unsafe_func(self, query, *args, **kwargs)

                curse(class_, func_name, safe_func)

    __completed = True
