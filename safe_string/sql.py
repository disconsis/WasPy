import sqlparse
import sqlvalidator
from safe_string import safe_string


def has_sqli(query):
    """
    Check if the query has an sql injection.
    """
    if not isinstance(query, safe_string):
        return True

    start_idx = 0
    for statement in sqlparse.parse(query):
        for token in statement.flatten():
            end_idx = start_idx + len(token.value)  # non-inclusive
            if token.ttype not in sqlparse.tokens.Literal and \
                    token.ttype not in sqlparse.tokens.Whitespace:
                # all chars should be trusted
                for char_idx in range(start_idx, end_idx):
                    if not query._trusted[char_idx]:
                        return True

            start_idx = end_idx

    return False


def is_valid_sql(query):
    """
    Simple sql validator.
    `sqlvalidator.is_valid` frequently throws errors
    on invalid input (like unbalanced quotes), so we wrap it in a bare `except`.
    """
    try:
        return sqlvalidator.parse(query).is_valid()
    except:
        return False
