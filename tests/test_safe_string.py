import string


from safe_string.safe_string import safe_string
from string import printable
import random
from bitarray import bitarray, frozenbitarray
import pytest
import types


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


# TODO: Check if can be removed
def test_can_initialize_with_custom_trusted():
    for length in range(100):
        unsafe = gen_random_string(length)
        trusted = gen_random_trusted(length)
        safe = safe_string(unsafe, trusted)
        assert safe == unsafe
        assert safe._trusted == trusted


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
    length = 100
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

def test_replace():
    unsafe = "abABabAB"
    unsafe_old = "AB"
    unsafe_new = "ab"

    safe = safe_string(unsafe, trusted=frozenbitarray([True, True, False, False, True, True, False, False]))
    old_str = safe_string(unsafe_old, frozenbitarray([False]*2))
    new_str = safe_string(unsafe_new, trusted=frozenbitarray([True]*2))

    assert unsafe.replace(unsafe_old, unsafe_new) == safe.replace(old_str, new_str)
    assert safe.replace(old_str, new_str)._trusted == frozenbitarray([True]*8)
    assert unsafe.replace(unsafe_old, unsafe_new, 1) == safe.replace(old_str, new_str, 1)
    assert safe.replace(old_str, new_str, 1)._trusted == frozenbitarray([True, True, True, True, True, True, False, False])

def test_count():
    unsafe = "abABabAB"
    unsafe_old1 = "AB"
    unsafe_old2 = "cd"

    safe = safe_string(unsafe, trusted=frozenbitarray([True, True, False, False, True, True, False, False]))
    old_str1 = safe_string(unsafe_old1, frozenbitarray([False]*2))
    old_str2 = safe_string(unsafe_old2, frozenbitarray([False]*2))

    assert safe.count(old_str1) == unsafe.count(unsafe_old1)
    assert safe.count(old_str2) == unsafe.count(unsafe_old2)

def test_find():
    unsafe = "abABabAB"
    unsafe_old1 = "AB"
    unsafe_old2 = "cd"

    safe = safe_string(unsafe, trusted=frozenbitarray([True, True, False, False, True, True, False, False]))
    old_str1 = safe_string(unsafe_old1, frozenbitarray([False]*2))
    old_str2 = safe_string(unsafe_old2, frozenbitarray([False]*2))

    assert safe.find(old_str1) == unsafe.find(unsafe_old1)
    assert safe.find(old_str2) == unsafe.find(unsafe_old2)
    assert safe.rfind(old_str1) == unsafe.rfind(unsafe_old1)
    assert safe.rfind(old_str2) == unsafe.rfind(unsafe_old2)

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


def test_lr_justification():
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

@pytest.mark.skip
def test_zfill_behaves_same_as_rjust():
    unsafe = gen_random_string(15)
    safe = gen_random_safe_from_unsafe(unsafe)
    for width in range(25):
        assert safe.zfill(width) == unsafe.zfill(width)


def test_center():
    unsafe_odd = "12345"
    unsafe_even = "123456"
    # meant to be untrusted to distinguish from original trusted string
    fillchar_safe = safe_string._new_untrusted("-")

    for unsafe in (unsafe_odd, unsafe_even):
        safe = safe_string._new_trusted(unsafe)
        for width in (0, 1, 5, 6, 7, 10, 11, 12):
            assert safe.center(width) == unsafe.center(width)
            assert safe.center(width, fillchar_safe) == unsafe.center(width, fillchar_safe)
            for char in safe.center(width, fillchar_safe):
                # fillchar is unsafe, rest everything is safe
                assert (char != fillchar_safe) == bool(char._trusted[0])

def test_partition():
    #Test-1
    u1 = gen_random_string(18)
    u_sep1 = u1[2:4]
    s1 = gen_random_safe_from_unsafe(u1)
    s_sep1 = s1[2:4]
    assert s1.partition(s_sep1) == u1.partition(u_sep1)
    assert s1.rpartition(s_sep1) == u1.rpartition(u_sep1)

    #Test-2
    u2 = "abab"
    u_sep2 = "xy"
    s2 = gen_random_safe_from_unsafe(u2)
    s_sep2 = gen_random_safe_from_unsafe(u_sep2)
    (before, sep, after) = u2.partition(u_sep2)
    assert s2.partition(s_sep2) == u2.partition(u_sep2)
    assert before == u2
    assert sep == safe_string("", frozenbitarray())
    assert after == safe_string("", frozenbitarray())
    (before, sep, after) = u2.rpartition(u_sep2)
    assert s2.rpartition(s_sep2) == u2.rpartition(u_sep2)
    assert before == safe_string("", frozenbitarray())
    assert sep == safe_string("", frozenbitarray())
    assert after == u2

    #Test-3
    u_sep3 = "ababa"
    s_sep3 = gen_random_safe_from_unsafe(u_sep3)
    (before, sep, after) = u2.partition(u_sep3)
    assert s2.partition(s_sep3) == u2.partition(u_sep3)
    assert before == u2
    assert sep == safe_string("", frozenbitarray())
    assert after == safe_string("", frozenbitarray())
    (before, sep, after) = u2.rpartition(u_sep3)
    assert s2.rpartition(s_sep3) == u2.rpartition(u_sep3)
    assert before == safe_string("", frozenbitarray())
    assert sep == safe_string("", frozenbitarray())
    assert after == u2

    #Test-4
    u4 = "ababab"
    u_sep4 = "ab"
    s4 = gen_random_safe_from_unsafe(u4)
    s_sep4 = gen_random_safe_from_unsafe(u_sep4)
    (before, sep, after) = u4.partition(u_sep4)
    assert s4.partition(s_sep4) == u4.partition(u_sep4)
    (before, sep, after) = u4.rpartition(u_sep4)
    assert s4.rpartition(s_sep4) == u4.rpartition(u_sep4)

def test_split():
    unsafe = "011110011010101011101010"
    safe = safe_string(unsafe, frozenbitarray(unsafe))
    for maxsplit in range(10):
        for chunk, chunk_unsafe in zip(safe.split("0", maxsplit), unsafe.split("0", maxsplit)):
            assert chunk == chunk_unsafe
            assert len(chunk) == len(chunk._trusted)
            for char in chunk:
                assert (char == "1") == bool(char._trusted[0])

        for chunk, chunk_unsafe in zip(safe.rsplit("0", maxsplit), unsafe.rsplit("0", maxsplit)):
            assert chunk == chunk_unsafe
            assert len(chunk) == len(chunk._trusted)
            for char in chunk:
                assert (char == "1") == bool(char._trusted[0])

    unsafe = "   11\t222 \n\r333  \n"
    trusted = frozenbitarray([
        not char.isspace()
        for char in unsafe
    ])
    safe = safe_string(unsafe, trusted)
    for maxsplit in range(5):
        for chunk, chunk_unsafe in zip(safe.split(None, maxsplit), unsafe.split(None, maxsplit)):
            assert chunk == chunk_unsafe
            assert len(chunk) == len(chunk._trusted)
            for char in chunk:
                assert not char.isspace() == bool(char._trusted[0])

        for chunk, chunk_unsafe in zip(safe.rsplit(None, maxsplit), unsafe.rsplit(None, maxsplit)):
            assert chunk == chunk_unsafe
            assert len(chunk) == len(chunk._trusted)
            for i, char in enumerate(chunk):
                assert not char.isspace() == bool(char._trusted[0])

    for _ in range(10):
        unsafe = gen_random_string(50)
        maxsplit = random.randint(5, 10)
        safe = gen_random_safe_from_unsafe(unsafe)
        assert safe.split(None, maxsplit) == unsafe.split(None, maxsplit)
        assert safe.split(unsafe[:2], maxsplit) == unsafe.split(unsafe[:2], maxsplit)
        assert safe.split(safe[:2], maxsplit) == unsafe.split(safe[:2], maxsplit)
        assert safe.split(unsafe[-2:], maxsplit) == unsafe.split(unsafe[-2:], maxsplit)
        assert safe.split(safe[-2:], maxsplit) == unsafe.split(safe[-2:], maxsplit)

        assert safe.rsplit(None, maxsplit) == unsafe.rsplit(None, maxsplit)
        assert safe.rsplit(unsafe[:2], maxsplit) == unsafe.rsplit(unsafe[:2], maxsplit)
        assert safe.rsplit(safe[:2], maxsplit) == unsafe.rsplit(safe[:2], maxsplit)
        assert safe.rsplit(unsafe[-2:], maxsplit) == unsafe.rsplit(unsafe[-2:], maxsplit)
        assert safe.rsplit(safe[-2:], maxsplit) == unsafe.rsplit(safe[-2:], maxsplit)


def test_expandtabs():
    untrusted = safe_string._new_untrusted("x")
    trusted_tab = safe_string._new_trusted("\t")

    for safe in (
        untrusted * 5,
        untrusted * 11 + trusted_tab,
        trusted_tab + untrusted * 11,
        trusted_tab + untrusted * 11 + trusted_tab,
        trusted_tab * 2 + untrusted * 11 + trusted_tab * 4,
        (
            untrusted * 10
            + trusted_tab
            + untrusted * 20
            + trusted_tab * 3
            + untrusted * 4
        ),
    ):

        unsafe = safe._to_unsafe_str()
        for tabsize in (0, 1, 2, 4, 5, 8):
            safe_expanded = safe.expandtabs(tabsize)
            assert safe_expanded == unsafe.expandtabs(tabsize)
            assert len(safe_expanded) == len(safe_expanded._trusted)
            for char in safe_expanded:
                # trusted only if expanded to " " from trusted "\t"
                if (char == " ") != bool(char._trusted[0]):
                    print(f"tabsize = {tabsize}")
                    safe._debug_repr()
                    safe.expandtabs(tabsize)._debug_repr()
                    raise

def test_join():
    # TODO: String test is skipped for now, check if necessary

    num_items = 5
    max_length = 10 

    def get_safe_iterable(string_list, trusted_list):
        for i in range(len(string_list)):
            yield safe_string(string_list[i], trusted=trusted_list[i])

    def get_unsafe_iterable(string_list):
        for i in range(len(string_list)):
            yield string_list[i]

    def gen_len_random_strings(num_items, max_length):
        str_list = []
        for i in range(random.randint(0, num_items)):
            length = random.randint(0, max_length)
            unsafe = gen_random_string(length)
            str_list.append(unsafe)
        return str_list

    join_list = ['']
    # TODO: Test for join using [',', '\n', 'abcd', '\t']

    for sep in join_list:
        print(f"===== SEP : {sep} =====")
        strings_list = [gen_len_random_strings(num_items, max_length) for i in range(num_items)]
        trusted_list = [[gen_random_trusted(len(string)) for string in string_list] for string_list in strings_list]

        unsafe_iterable_list = [
            list(get_unsafe_iterable(strings_list[0])),
            get_unsafe_iterable(strings_list[1]),
            set(get_unsafe_iterable(strings_list[2])),
            tuple(get_unsafe_iterable(strings_list[3])),
            dict((safe_str, i) for i, safe_str in enumerate(get_unsafe_iterable(strings_list[4])))
        ]

        safe_iterable_list = [
            list(get_safe_iterable(strings_list[0], trusted_list[0])),
            get_safe_iterable(strings_list[1], trusted_list[1]),
            set(get_safe_iterable(strings_list[2], trusted_list[2])),
            tuple(get_safe_iterable(strings_list[3], trusted_list[3])),
            dict((safe_str, i) for i, safe_str in enumerate(get_safe_iterable(strings_list[4], trusted_list[4])))
        ]

        for i in range(len(strings_list)):
            print("=== ITERABLE ===")
            safe_iterable = safe_iterable_list[i]
            unsafe_iterable = unsafe_iterable_list[i]

            regenerate_iterable = False
            if isinstance(safe_iterable, types.GeneratorType):
                regenerate_iterable = True
            safe_join = safe_string(sep, trusted=gen_random_trusted(len(sep))).join(safe_iterable)
            unsafe_join = sep.join(unsafe_iterable)
            trusted_join = bitarray()

            # TODO: Find better way to combine, couldn't do with list comprehension
            if regenerate_iterable:
                safe_iterable = get_safe_iterable(strings_list[i], trusted_list[i])
            for safe_str in safe_iterable:
                trusted_join += safe_str._trusted
            trusted_join = frozenbitarray(trusted_join)

            assert unsafe_join == safe_join
            assert trusted_join == safe_join._trusted
            assert len(unsafe_join) == len(safe_join._trusted)

def test_splitlines():
    unsafe = gen_random_string(20)
    trusted = gen_random_trusted(20)
    safe = safe_string(unsafe, trusted=trusted)

    unsafe_split = unsafe.splitlines()
    safe_split = safe.splitlines()

    start = 0

    for unsafe_slice, safe_slice in zip(unsafe_split, safe_split):
        assert unsafe_slice == safe_slice._to_unsafe_str()
        assert trusted[start:start+len(unsafe_slice)] == safe._trusted[start:start+len(safe_slice)]
        start += len(unsafe_slice)+1
