from forbiddenfruit import curse
import sqlite3
import psycopg2
import mysql.connector
from functools import wraps
import ast
from ast import AST

from safe_string import safe_string
import sql

__completed = False


def wrap_execute(class_, unsafe_func, error_class):
    @wraps(unsafe_func)
    def safe_func(self, query, *args, **kwargs):
        # print(f'DEBUG: calling {class_.__module__}.{unsafe_func.__name__}')
        if sql.sqli(query):
            print("[!] SQLi detected in {}".format(class_.__module__))
            print(f"query: {query!r}")
            raise error_class("sqli detected")

        return unsafe_func(self, query, *args, **kwargs)

    return safe_func


class ToUnsafeVisitor(ast.NodeTransformer):
    def generic_visit(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item)

                        setattr(node, field, item._to_unsafe_str())

            elif isinstance(value, AST):
                self.visit(value)

            elif isinstance(value, safe_string):
                setattr(node, field, value._to_unsafe_str())


if not __completed:
    unsafe_execute_classes = [
        (sqlite3.Connection, sqlite3.Error),
        (sqlite3.Cursor, sqlite3.Error),
        (psycopg2.extensions.cursor, psycopg2.OperationalError),
        (mysql.connector.cursor.MySQLCursor, mysql.connector.Error),
    ]

    if mysql.connector.HAVE_CEXT:
        unsafe_execute_classes.append(
            (mysql.connector.cursor_cext.CMySQLCursor, mysql.connector.Error)
        )


    for class_, error_class in unsafe_execute_classes:
        for func_name in ("execute", "executemany"):
            try:
                unsafe_func = getattr(class_, func_name)
            except AttributeError:
                pass
            else:
                safe_func = wrap_execute(class_, unsafe_func, error_class)
                curse(class_, func_name, safe_func)



    orig_compile = compile

    @wraps(compile)
    def safe_compile(source, *args, **kwargs):
        if isinstance(source, safe_string):
            source = source._to_unsafe_str()

        elif isinstance(source, ast.AST):
            ToUnsafeVisitor().visit(source)

        try:
            return orig_compile(source, *args, **kwargs)
        except TypeError:
            print(ast.dump(source))
            raise

    __builtins__["compile"] = safe_compile



    __completed = True
