#!/usr/bin/env python3


from safe_string.safe_string import safe_string
from string import printable
import random
from bitarray import frozenbitarray


def gen_random_string(length):
    return "".join(random.choices(printable, k=length))


def gen_random_trusted(length):
    return frozenbitarray(random.choices([True, False], k=length))


def gen_random_safe_string(length):
    return safe_string(gen_random_string(length), trusted=gen_random_trusted(length))


def gen_random_safe_from_unsafe(string):
    return safe_string(string, trusted=gen_random_trusted(len(string)))


def test_can_create_new_safe_strings():
    for length in range(100):
        unsafe = gen_random_string(length)
        safe_string(unsafe)


def test_default_trusted_is_same_length_as_string():
    safe = gen_random_safe_string(100)
    assert len(safe._trusted) == len(safe.string)


def test_can_initialize_with_custom_trusted():
    safe_string(printable, trusted=frozenbitarray([True] * len(printable)))


def test_safe_strings_return_correct_values_for_string_to_non_string_functions():
    s1 = gen_random_safe_string(18)
    s2 = gen_random_safe_string(20)

    assert len(safe_string(s1)) == len(s1)
    assert len(safe_string(s2)) == len(s2)

    assert (s1 == s2) == (safe_string(s1) == safe_string(s2))
    assert (s1 < s2) == (safe_string(s1) < safe_string(s2))
    assert (s1 > s2) == (safe_string(s1) > safe_string(s2))
    assert (s1 <= s2) == (safe_string(s1) <= safe_string(s2))
    assert (s1 >= s2) == (safe_string(s1) >= safe_string(s2))

    assert s1.isascii() == safe_string(s1).isascii()
    assert s1.islower() == safe_string(s1).islower()
    assert s1.isupper() == safe_string(s1).isupper()
    assert s1.istitle() == safe_string(s1).istitle()
    assert s1.isspace() == safe_string(s1).isspace()
    assert s1.isdecimal() == safe_string(s1).isdecimal()
    assert s1.isdigit() == safe_string(s1).isdigit()
    assert s1.isnumeric() == safe_string(s1).isnumeric()
    assert s1.isalpha() == safe_string(s1).isalpha()
    assert s1.isalnum() == safe_string(s1).isalnum()
    assert s1.isidentifier() == safe_string(s1).isidentifier()
    assert s1.isprintable() == safe_string(s1).isprintable()


def test_string_to_same_length_string_functions_dont_change_trusted():
    s = gen_random_safe_string(100)

    assert s.capitalize()._trusted == s._trusted
    assert s.upper()._trusted == s._trusted
    assert s.lower()._trusted == s._trusted
    assert s.lower()._trusted == s._trusted
    assert s.title()._trusted == s._trusted
    assert s.swapcase()._trusted == s._trusted


def test_substring_finding_functions_work_correctly():
    haystack = "abcdefghideffoo"
    needle1 = "def"
    needle2 = "df"
    start = "abcde"
    end = "oo"

    assert (needle1 in haystack) == (safe_string(needle1) in safe_string(haystack))
    assert (needle2 in haystack) == (safe_string(needle2) in safe_string(haystack))

    assert haystack.index(haystack[4:7]) == safe_string(haystack).index(safe_string(haystack[4:7]))
    assert haystack.rindex(haystack[4:7]) == safe_string(haystack).rindex(safe_string(haystack[4:7]))

    assert haystack.startswith(start) == safe_string(haystack).startswith(
        safe_string(start)
    )
    assert haystack.startswith(end) == safe_string(haystack).startswith(
        safe_string(end)
    )
    assert haystack.endswith(start) == safe_string(haystack).endswith(
        safe_string(start)
    )
    assert haystack.endswith(end) == safe_string(haystack).endswith(safe_string(end))


def test_substrings_are_returned_correctly():
    length = 1000
    string = gen_random_string(length)
    trusted = gen_random_trusted(length)
    safe = safe_string(string, trusted=trusted)

    for i in range(-(length + 5), (length + 5)):
        for j in range(-(length + 5), (length + 5)):
            sub = safe[i:j]
            assert sub.string == string[i:j]
            assert sub._trusted == trusted[i:j]


def test_safe_string_format():
    template = gen_random_safe_from_unsafe("my name is {name} the {0}nd")
    name = gen_random_safe_from_unsafe("ramses")
    formatted = template.format(2, name=name)
    assert formatted.string == "my name is ramses the 2nd"
    assert formatted._trusted == (
        template._trusted[: len("my name is ")]
        + name._trusted
        + template._trusted[len("my name is {name}") : len("my name is {name} the ")]
        + [False]
        + template._trusted[len("my name is {name} the {0}") :]
    )
