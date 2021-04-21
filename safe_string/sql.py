import sqlparse
from safe_string import safe_string #, dbg_print_safestring

def has_sqli(query):
    if not isinstance(query, safe_string):
        return True

    start_idx = 0
    for statement in sqlparse.parse(query):
        for token in statement.flatten():
            end_idx = start_idx + len(token.value) # non-inclusive
            if token.ttype not in sqlparse.tokens.Literal and \
                    token.ttype not in sqlparse.tokens.Whitespace:
                # all chars should be trusted
                for char_idx in range(start_idx, end_idx):
                    if not query._trusted[char_idx]:
                        print("failed at token", str(token))
                        return True

            start_idx = end_idx

    return False


if __name__ == "__main__":
    query_string = "SELECT * FROM tbl WHERE id = 1;"
    query_trusted = [True] * len(query_string)
    print(has_sqli(safe_string(query_string, trusted=query_trusted)))

    query_string = "SELECT * FROM tbl WHERE id = 1;"
    query_trusted = [False] * len(query_string)
    print(has_sqli(safe_string(query_string, trusted=query_trusted)))

    def check_sqli(query_string, trust_string):
        trusted = list(map(lambda x: bool(int(x)), trust_string))
        query = safe_string(query_string, trusted=trusted)
        print(has_sqli(query))

    check_sqli(
        "SELECT * FROM tbl WHERE id = 1;",
        "1111111111111111111111111111101"
    )

    check_sqli(
        "SELECT * FROM tbl WHERE id = 1; SELECT * FROM tbl;",
        "11111111111111111111111111111000000000000000000001"
    )

    check_sqli(
        "SELECT * FROM customers WHERE account = '' or '1' = '1';",
        "11111111111111111111111111111111111111111000000000000011"
    )

    check_sqli(
        "SELECT acct FROM users WHERE login='admin' -- ' AND pin=0",
        "111111111111111111111111111111111111000000000011111111110"
    )

    check_sqli(
        "SELECT acct FROM users WHERE account_id = 1234 ",
        "11111111111111111111111111111111111111111100000"
    )

    for template in [
        "SELECT * FROM users WHERE name = '{}'",
        "SELECT * FROM users WHERE id = {}",
    ]:
        template_sf = safe_string(template, trusted=[True] * len(template))
        for user_input in [
                "1'1", # check
                "1 exec sp_ (or exec xp_)",
                "1 and 1=1",
                "1' and 1=(select count(*) from tablenames); --",
                "1 or 1=1",
                "1' or '1'='1",
                "1or1=1",
                "1'or'1'='1",
                "fake@ema'or'il.nl'='il.nl",
        ]:
            user_input_sf = safe_string._new_untrusted(user_input)
            query = template_sf.replace(safe_string._new_untrusted("{}"),
                                        user_input_sf)
            print('-----------------------------')
            # dbg_print_safestring(query)
            print(has_sqli(query))
            print('-----------------------------')
            input()
