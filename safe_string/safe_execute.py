"""

sqlite3

override sqlite3.Connection.execute()

"""

from forbiddenfruit import curse
import sqlite3
import sql
import psycopg2 


sqlite3_unsafe_execute = sqlite3.Connection.execute
sqlite3_unsafe_executemany = sqlite3.Connection.executemany
psycopg2_unsafe_execute = psycopg2.extensions.cursor.execute
psycopg2_unsafe_executemany = psycopg2.extensions.cursor.executemany 

def psycopg2_safe_execute(connection, query, *args, **kwargs):
    # print(f"sqlite3 -- query: {query!r} args: {args!r}")
    if sql.sqli(query):
        print("[!] SQLi detected in psycopg2")
        print(f"query: {query!r}")
        return

    return psycopg2_unsafe_execute(connection, query, *args, **kwargs)

def psycopg2_safe_executemany(connection, query, *args, **kwargs):
    # print(f"sqlite3 -- query: {query!r} args: {args!r}")
    if sql.sqli(query):
        print("[!] SQLi detected in psycopg2")
        print(f"query: {query!r}")
        return

    return psycopg2_unsafe_executemany(connection, query, *args, **kwargs)

def sqlite3_safe_execute(connection, query, *args):
    # print(f"sqlite3 -- query: {query!r} args: {args!r}")
    if sql.sqli(query):
        print("[!] SQLi detected in sqlite3")
        print(f"query: {query!r}")
        return

    return sqlite3_unsafe_execute(connection, query, *args)

def sqlite3_safe_executemany(connection, query, *args):
    # print(f"sqlite3 -- query: {query!r} args: {args!r}")
    if sql.sqli(query):
        print("[!] SQLi detected in sqlite3")
        print(f"query: {query!r}")
        return

    return sqlite3_unsafe_executemany(connection, query, *args)


curse(sqlite3.Connection, "execute", sqlite3_safe_execute)
curse(sqlite3.Connection, "executemany", sqlite3_safe_executemany)
curse(psycopg2.extensions.cursor, "execute", psycopg2_safe_execute)
curse(psycopg2.extensions.cursor, "executemany", psycopg2_safe_executemany)
