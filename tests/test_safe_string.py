import string


from safe_string.safe_string import safe_string
from string import printable
import random
from bitarray import frozenbitarray
import pytest


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
        trusted = gen_random_trusted(length)
        safe_string(unsafe, trusted)


def test_default_trusted_is_same_length_as_string():
    safe = gen_random_safe_string(100)
    assert len(safe._trusted) == len(safe)


def test_can_initialize_with_custom_trusted():
    safe_string(printable, trusted=frozenbitarray([True] * len(printable)))


def test_safe_strings_return_correct_values_for_string_to_non_string_functions():
    u1 = gen_random_string(18)
    u2 = gen_random_string(20)
    s1 = gen_random_safe_from_unsafe(u1)
    s2 = gen_random_safe_from_unsafe(u2)

    assert len(s1) == len(u1)
    assert len(s2) == len(u2)

    assert (s1 == s2) == (u1 == u2)
    assert (s1 < s2) == (u1 < u2)
    assert (s1 > s2) == (u1 > u2)
    assert (s1 <= s2) == (u1 <= u2)
    assert (s1 >= s2) == (u1 >= u2)

    assert s1.isascii() == u1.isascii()
    assert s1.islower() == u1.islower()
    assert s1.isupper() == u1.isupper()
    assert s1.istitle() == u1.istitle()
    assert s1.isspace() == u1.isspace()
    assert s1.isdecimal() == u1.isdecimal()
    assert s1.isdigit() == u1.isdigit()
    assert s1.isnumeric() == u1.isnumeric()
    assert s1.isalpha() == u1.isalpha()
    assert s1.isalnum() == u1.isalnum()
    assert s1.isidentifier() == u1.isidentifier()
    assert s1.isprintable() == u1.isprintable()


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

    safe_haystack = gen_random_safe_from_unsafe(haystack)
    safe_needle1 = gen_random_safe_from_unsafe(needle1)
    safe_needle2 = gen_random_safe_from_unsafe(needle2)
    safe_start = gen_random_safe_from_unsafe(start)
    safe_end = gen_random_safe_from_unsafe(end)

    assert (needle1 in haystack) == (safe_needle1 in safe_haystack)
    assert (needle2 in haystack) == (safe_needle2 in safe_haystack)

    assert haystack.index(haystack[4:7]) == safe_haystack.index(safe_haystack[4:7])
    assert haystack.rindex(haystack[4:7]) == safe_haystack.rindex(safe_haystack[4:7])

    assert haystack.startswith(start) == safe_haystack.startswith(safe_start)
    assert haystack.startswith(end) == safe_haystack.startswith(safe_end)
    assert haystack.endswith(start) == safe_haystack.endswith(safe_start)
    assert haystack.endswith(end) == safe_haystack.endswith(safe_end)


def test_substrings_are_returned_correctly():
    length = 1000
    string = gen_random_string(length)
    trusted = gen_random_trusted(length)
    safe = safe_string(string, trusted=trusted)

    for i in range(-(length + 5), (length + 5)):
        for j in range(-(length + 5), (length + 5)):
            sub = safe[i:j]
            assert sub == string[i:j]
            assert sub._trusted == trusted[i:j]


@pytest.mark.skip
def test_safe_string_format():
    template = gen_random_safe_from_unsafe("my name is {name} the {0}nd")
    name = gen_random_safe_from_unsafe("ramses")
    formatted = template.format(2, name=name)
    assert formatted == "my name is ramses the 2nd"
    assert formatted._trusted == (
        template._trusted[: len("my name is ")]
        + name._trusted
        + template._trusted[len("my name is {name}") : len("my name is {name} the ")]
        + [False]
        + template._trusted[len("my name is {name} the {0}") :]
    )


def test_getitem():
    def make_array(item):
        if isinstance(item, frozenbitarray):
            return item
        else:
            return frozenbitarray([item])

    unsafe = gen_random_string(100)
    safe = gen_random_safe_from_unsafe(unsafe)
    for key in (5, slice(5, 40), slice(45, 40)):
        assert isinstance(safe[key], safe_string)
        assert safe[key] == unsafe[key]
        assert safe[key]._trusted == make_array(safe._trusted[key])


def test_iter():
    safe = gen_random_safe_string(100)
    for idx, safe_char in enumerate(safe):
        assert safe_char == safe[idx]
        assert safe_char._trusted == frozenbitarray([safe._trusted[idx]])


def test_repr_same_length():
    examples = [
        "abc",
        "\\",
        "\n",
        b"Ni\xc3\xb10".decode("utf-8"),
        string.printable,
        "\x0c",
        "\x1c",
        "\x2c",
        "\xff",
        "\xf8",
        "\x7f\x8f\x9f\xff",
        "\f",
        "\t",
        " ",
        "",
    ]
    for unsafe in examples:
        # safe = gen_random_safe_from_unsafe(unsafe)
        safe = safe_string(unsafe, frozenbitarray([True, False] * (len(unsafe) // 2) + [True] * (len(unsafe) % 2)))
        safe_repr = repr(safe)
        assert len(safe_repr) == len(repr(unsafe))
        if len(safe_repr) != len(safe_repr._trusted):
            safe._debug_repr()
            safe_repr._debug_repr()
            assert False


def test_add():
    for _ in range(10):
        first = gen_random_safe_string(50)
        second = gen_random_safe_string(60)
        sum_ = first + second
        assert sum_ == first + second
        assert sum_._trusted == first._trusted + second._trusted


def test_mul_and_rmul():
    for _ in range(10):
        orig = gen_random_safe_string(50)
        n = random.randint(5, 10)
        mult_l = orig * n
        mult_r = n * orig
        assert orig._to_unsafe_str() * n == mult_l._to_unsafe_str()
        assert orig._trusted * n == mult_l._trusted
        assert n * orig._to_unsafe_str() == mult_r._to_unsafe_str()
        assert n * orig._trusted == mult_r._trusted


def test_strip():
    unsafe = "\n blah\nfoo\t\r\f foo \r \t"
    safe = gen_random_safe_from_unsafe(unsafe)
    assert safe.lstrip() == unsafe.lstrip()
    assert safe.lstrip()._trusted == safe._trusted[2:]
    assert safe.rstrip() == unsafe.rstrip()
    assert safe.rstrip()._trusted == safe._trusted[:-4]
    assert safe.strip() == unsafe.strip()
    assert safe.strip()._trusted == safe._trusted[2:-4]


def test_justification():
    unsafe = gen_random_string(15)
    safe = gen_random_safe_from_unsafe(unsafe)
    fillchar_trusted = safe_string._new_trusted("-")

    for width in (10, 15, 20, 25):
        assert safe.ljust(width) == unsafe.ljust(width)
        assert safe.ljust(width, fillchar_trusted) == unsafe.ljust(width, "-")
        assert safe.rjust(width) == unsafe.rjust(width)
        assert safe.rjust(width, fillchar_trusted) == unsafe.rjust(width, "-")

    for width in (0, 10, 15):
        assert safe.ljust(width)._trusted == safe._trusted
        assert safe.ljust(width, fillchar_trusted)._trusted == safe._trusted
        assert safe.rjust(width)._trusted == safe._trusted
        assert safe.rjust(width, fillchar_trusted)._trusted == safe._trusted

    for width in (16, 20, 25):
        false_array = frozenbitarray([False] * (width - 15))
        true_array = frozenbitarray([True] * (width - 15))
        assert safe.ljust(width)._trusted == safe._trusted + false_array
        assert safe.rjust(width)._trusted == false_array + safe._trusted
        assert safe.ljust(width, fillchar_trusted)._trusted == safe._trusted + true_array
        assert safe.rjust(width, fillchar_trusted)._trusted == true_array + safe._trusted
