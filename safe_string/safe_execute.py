"""

sqlite3

override sqlite3.Connection.execute()

"""

from forbiddenfruit import curse
import sqlite3
import sql


sqlite3_unsafe_execute = sqlite3.Connection.execute
sqlite3_unsafe_executemany = sqlite3.Connection.executemany

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
