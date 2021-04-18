import math


class OverrideUnsafe:
    def __init__(self, safe_obj):
        self.obj = safe_obj

    def __format__(self, *args, **kwargs):
        if isinstance(self.obj, safe_string):
            result = safe_format(self.obj, *args, **kwargs)
        else:
            result = self.obj.__format__(*args, **kwargs)

        if isinstance(result, safe_string):
            return result.string
        else:
            return result

    def __repr__(self):
        result = self.obj.__repr__()
        if isinstance(result, safe_string):
            return result.string
        else:
            return result

    def __str__(self):
        result = self.obj.__str__()
        if isinstance(result, safe_string):
            return result.string
        else:
            return result

    def __getitem__(self, *args, **kwargs):
        return OverrideUnsafe(self.obj.__getitem__(*args, **kwargs))

    def __getattr__(self, *args, **kwargs):
        return OverrideUnsafe(self.obj.__getattribute__(*args, **kwargs))


def safe_format(fmt_string, *args, **kwargs):
    if not isinstance(fmt_string, safe_string):
        fmt_string = safe_string(fmt_string)
    unsafe_args = list(map(OverrideUnsafe, args))
    unsafe_kwargs = {key: OverrideUnsafe(value)
                     for key, value in kwargs.items()}

    result_string = fmt_string.string.format(*unsafe_args, **unsafe_kwargs)
    arg_holes, all_holes = _do_build_string(fmt_string)
    arg_hole_trusts = render_field(arg_holes, fmt_string, args, kwargs)
    final_trusted = construct_trusted(fmt_string, all_holes, arg_hole_trusts)
    if len(result_string) != len(final_trusted):
        print("ERROR:")
        dbg_print_safestring(safe_string(result_string, trusted=final_trusted))
        print(
            f"str len = {len(result_string)} | trust len = {len(final_trusted)}")
        raise Exception("mismatched lengths")
    return safe_string(result_string, trusted=final_trusted)


def _do_build_string(s):
    isHole = False
    res = []
    holes = []
    lb_loc = 0
    i = 0

    while i < len(s):
        if s[i] == '{':
            if i < len(s)-1 and s[i+1] == '{':
                res.append(('l', (i, i+1)))
                isHole = False
                i += 1
            else:
                isHole = True
                lb_loc = i
        elif s[i] == '[':
            while s[i] != ']':
                i += 1
        elif s[i] == '}':
            if isHole:
                res.append(('h', (lb_loc, i)))
                holes.append((lb_loc, i))
                isHole = False
            elif i < len(s)-1 and s[i+1] == '}':
                res.append(('r', (i, i+1)))
                i += 1
        i += 1

    return holes, res


def render_field(holes, fmt_string, args, kwargs):
    result = []
    parser = field_parser(args, kwargs)
    for hole in holes:
        value, conv, spec = parser(fmt_string[hole[0]:hole[1] + 1])
        if not isinstance(spec, safe_string):
            spec = safe_string(spec)
        s = value
        is_safe = False
        if isinstance(value, safe_string):
            is_safe = True
            s = value.string

        if conv == 'r':
            trusted = value.__repr__().trusted if is_safe else [
                False]*len(repr(s).__format__(spec.string))
            result.append(trusted)
        elif conv == 's':
            trusted = value.__str__().trusted if is_safe else [
                False]*len(str(s).__format__(spec.string))
            result.append(trusted)
        elif conv == 'a':
            if not is_safe:
                trusted = [False] * len(ascii(value))
            elif value.isascii():
                trusted = [False] + value.trusted + [False]
            else:
                # go char-by-char and call ascii
                trusted = []
                for char in value:
                    newchar = ascii(char.string)[1:-1]  # remove quotes
                    trusted += len(newchar) * char.trusted
                trusted = [False] + trusted + [False]  # for quotes

            result.append(trusted)
        else:
            trusted = value.trusted if is_safe else [
                False]*len(s.__format__(spec.string))
            result.append(trusted)

    return result


def construct_trusted(format_string, gl_holes, trusted_result):
    prev_index = 0
    gl_index = 0
    hl_index = 0
    final_trusted = []
    while gl_index < len(gl_holes):
        start = gl_holes[gl_index][1][0]
        end = gl_holes[gl_index][1][1]
        final_trusted += format_string.trusted[prev_index:start]
        new_trusted = []
        if gl_holes[gl_index][0] == 'l' or gl_holes[gl_index][0] == 'r':
            new_trusted += [format_string.trusted[end]]
        else:
            new_trusted += trusted_result[hl_index]
            hl_index += 1
        final_trusted += new_trusted
        gl_index += 1
        prev_index = end+1

    final_trusted += format_string.trusted[prev_index:]

    return final_trusted


test_cases = ["{abc}", "{{", "}}", "{{{}}}", "{}{}{}", "}", "{{{{}}}}"]
for s in test_cases:
    _do_build_string(s)


def parse_field(hole):
    hole = hole[1:-1]

    end = len(hole)
    i = 0
    while i < end:
        c = hole[i]
        if c == "!":
            # <name>  !  <conv>   :   <spec>
            #         i   i+1    i+2  i+3...
            name = hole[:i]
            conversion = hole[i + 1]
            if i + 2 < end:
                # then :<spec> exists
                spec = hole[i+3:]
            else:
                spec = safe_string("")

            return name, conversion, spec

        elif c == ":":
            # <name>  :  <spec>
            #         i  i+1...
            name = hole[:i]
            spec = hole[i+1:]

            return name, None, spec

        elif c == "[":
            while hole[i] != "]":
                i += 1

        i += 1

    # no : or ! encountered
    return hole, None, ""


def get_argument(args, kwargs):
    auto_numbering = -1

    def _get_argument(name):
        nonlocal auto_numbering

        i = 0
        end = len(name)
        while i < end and name[i] not in ("[", "."):
            i += 1

        index = name[:i]
        if not index:
            auto_numbering += 1
            return args[auto_numbering]
        elif index.isnumeric():
            return args[int(index)]
        else:
            return kwargs[index]

    return _get_argument


def resolve_lookups(obj, name):
    end = len(name)

    i = 0
    while i < end and name[i] not in ("[", "."):
        i += 1

    while i < end:
        c = name[i]
        if c == ".":
            i += 1
            start = i
            while i < end:
                if name[i] in (".", "["):
                    break
                i += 1
            attr = name[start:i]
            obj = getattr(obj, attr)

        elif c == "[":
            i += 1
            start = i
            while i < end:
                if name[i] == "]":
                    break
                i += 1
            index = name[start:i]
            i += 1  # skip the ']'
            if index.isnumeric():
                index = int(index)
            obj = obj[index]

    return obj


def field_parser(args, kwargs):
    get_arg = get_argument(args, kwargs)

    def _parser(hole):
        name, conv, spec = parse_field(hole)
        obj = get_arg(name)
        obj = resolve_lookups(obj, name)
        return obj, conv, spec

    return _parser


class safe_string:
    def __new__(cls, string, trusted=None):
        return super(safe_string, cls).__new__(cls)

    def __init__(self, string, trusted=None):
        self.string = string
        self.trusted = (
            trusted if trusted is not None
            else [False for _ in self.string]
        )

    def __le__(self, other):
        return self.string.__le__(other.string)

    def __lt__(self, other):
        return self.string.__lt__(other.string)

    def __eq__(self, other):
        if isinstance(other, safe_string):
            return self.string.__eq__(other.string)
        else:
            return self.string.__eq__(other)

    def __ne__(self, other):
        if isinstance(other, safe_string):
            return self.string.__ne__(other.string)
        else:
            return self.string.__ne__(other)

    def __ge__(self, other):
        return self.string.__ge__(other.string)

    def __gt__(self, other):
        return self.string.__gt__(other.string)

    def __contains__(self, subs):
        return self.string.__contains__(subs.string)

    def __hash__(self):
        return self.string.__hash__()

    def title(self):
        return safe_string(
            self.string.title(),
            trusted=self.trusted)

    def isascii(self):
        return self.string.isascii()

    def istitle(self):
        return self.string.istitle()

    def isdigit(self):
        return self.string.isdigit()

    def isalnum(self):
        return self.string.isalnum()

    def index(self, subs, *args, **kwargs):
        return self.string.index(subs.string, *args, **kwargs)

    def rindex(self, subs, *args, **kwargs):
        return self.string.index(subs.string, *args, **kwargs)

    def expandtabs(self, tabsize=8):
        string = ""
        trusted = []
        for i in range(len(self.string)):
            if self.string[i] == '\t':
                string += " " * tabsize
                trusted += [self.trusted[i]] * tabsize
            else:
                string += self.string[i]
                trusted += [self.trusted[i]]
        return safe_string(
            string,
            trusted=trusted)

    def lstrip(self, chars=None):
        string = self.string.lstrip(chars)
        return safe_string(
            string,
            trusted=self.trusted[-len(string):])

    def rstrip(self, chars=None):
        new_str = self.string.rstrip(chars)
        return safe_string(
            new_str,
            trusted=self.trusted[:len(new_str)])

    def strip(self, chars=None):
        return self.lstrip(chars).rstrip(chars)

    # TODO cleanup: fillchar is always safe_string
    def ljust(self, width, fillchar=' '):
        if isinstance(fillchar, safe_string):
            char_trust = fillchar.trusted[0]
            string = self.string.ljust(width, fillchar.string)
        else:
            char_trust = False
            string = self.string.ljust(width, fillchar)
        trusted = self.trusted + max(0, (width-len(self.string)))*[char_trust]
        return safe_string(
            string,
            trusted=trusted)

    # TODO cleanup: fillchar is always safe_string
    def rjust(self, width, fillchar=' '):
        if isinstance(fillchar, safe_string):
            char_trust = fillchar.trusted[0]
            string = self.string.rjust(width, fillchar.string)
        else:
            char_trust = False
            string = self.string.rjust(width, fillchar)
        trusted = self.trusted if ((len(string)-len(self.string)) <= 0) else [
            char_trust]*(len(string)-len(self.string)) + self.trusted
        return safe_string(
            string,
            trusted=trusted)

    def zfill(self, width):
        string = self.string.zfill(width)
        trusted = self.trusted if ((len(string)-len(self.string)) <= 0) else [
            False]*(len(string)-len(self.string)) + self.trusted
        return safe_string(
            string,
            trusted=trusted)

    def splitlines(self, keepends=False):
        safe_string_list = []
        start = 0
        for i in range(len(self.string)):
            if self.string[i] == '\n':
                safe_string_list.append(self[start:i+1]
                                        if keepends
                                        else self[start:i])
                start = i+1

        if start < len(self.string):
            safe_string_list.append(self[start:])
        return safe_string_list

    def startswith(self, prefix, *args, **kwargs):
        return self.string.startswith(prefix.string, *args, **kwargs)

    def endswith(self, suffix, *args, **kwargs):
        return self.string.endswith(suffix.string, *args, **kwargs)

    def __getitem__(self, key):
        # call __getitem__ on self.string first
        # to return the appropriate error
        new_string = self.string[key]
        if isinstance(key, int):
            return safe_string(new_string, trusted=[self.trusted[key]])
        elif isinstance(key, slice):
            return safe_string(new_string, trusted=self.trusted[key])
        else:
            raise TypeError("Invalid indexing")

    def __iter__(self):
        for char, trust in zip(self.string, self.trusted):
            yield safe_string(char, trusted=[trust])

    def __len__(self):
        return self.string.__len__()

    def __add__(self, other):
        return safe_string(
            self.string + other.string,
            trusted=self.trusted + other.trusted)

    def __mul__(self, num):
        return safe_string(
            self.string * num,
            trusted=self.trusted * num
        )

    def __rmul__(self, num):
        return self.__mul__(num)

    def replace(self, old, new, count=math.inf):
        final = safe_string("")
        start_idx = 0
        while count > 0:
            idx = self.string.find(old.string, start_idx)
            if idx == -1:
                break
            else:
                final += self[start_idx:idx] + new
                start_idx = idx + len(old)
                count -= 1

        final += self[start_idx:]
        return final

    def split(self, sep=None, maxsplit=-1):
        str_splits = self.string.split(sep=sep, maxsplit=maxsplit)
        result = []

        start_idx = 0
        if sep is None:
            while start_idx < len(self.string) \
                    and self.string[start_idx].isspace():
                start_idx += 1

        for elem in str_splits:
            elem_trusted = self.trusted[start_idx:start_idx + len(elem)]
            result.append(safe_string(elem, trusted=elem_trusted))

            start_idx += len(elem)
            if sep is None:
                while start_idx < len(self.string) \
                        and self.string[start_idx].isspace():
                    start_idx += 1
            else:
                start_idx += len(sep)

        return result

    def rsplit(self, sep=None, maxsplit=-1):
        str_splits = self.string.rsplit(sep=sep, maxsplit=maxsplit)
        result = []

        start_idx = 0
        if sep is None:
            while start_idx < len(self.string) \
                    and self.string[start_idx].isspace():
                start_idx += 1

        for elem in str_splits:
            elem_trusted = self.trusted[start_idx:start_idx + len(elem)]
            result.append(safe_string(elem, trusted=elem_trusted))

            start_idx += len(elem)
            if sep is None:
                while start_idx < len(self.string) \
                        and self.string[start_idx].isspace():
                    start_idx += 1
            else:
                start_idx += len(sep)

        return result

    def capitalize(self):
        return safe_string(self.string.capitalize(), trusted=self.trusted)

    # TODO cleanup: fillchar is always safe_string
    def center(self, width, fillchar=' '):
        if len(self) >= width:
            return self

        if isinstance(fillchar, safe_string):
            char_trust = fillchar.trusted[0]
            string = self.string.center(width, fillchar.string)
        else:
            char_trust = False
            string = self.string.center(width, fillchar)

        marg = width - len(self)
        left_fill = (marg // 2 + (marg & width & 1)) * [char_trust]
        right_fill = (marg - len(left_fill)) * [char_trust]
        trusted = left_fill + self.trusted + right_fill
        return safe_string(
            string,
            trusted=trusted)

    def find(self, sub, *args):
        return self.string.find(sub, *args)

    def join(self, seq):
        seq = iter(seq)

        def make_safe(elem):
            if isinstance(elem, safe_string):
                return elem
            else:
                return safe_string(elem)

        try:
            first_elem = next(seq)
            final = make_safe(first_elem)
        except StopIteration:
            return safe_string("")

        for elem in seq:
            final += self + make_safe(elem)

        return final

    def rfind(self, sub, *args):
        return self.string.rfind(sub, *args)

    def upper(self):
        return safe_string(self.string.upper(), trusted=self.trusted)

    def lower(self):
        return safe_string(self.string.lower(), trusted=self.trusted)

    def swapcase(self):
        return safe_string(self.string.swapcase(), trusted=self.trusted)

    def islower(self):
        return self.string.islower()

    def isupper(self):
        return self.string.isupper()

    def isspace(self):
        return self.string.isspace()

    def isdecimal(self):
        return self.string.isdecimal()

    def isidentifier(self):
        return self.string.isidentifier()

    def isnumeric(self):
        return self.string.isnumeric()

    def isalpha(self):
        return self.string.isalpha()

    def isprintable(self):
        return self.string.isprintable()

    def __str__(self):
        return self

    def __repr__(self):
        return safe_string(repr(self.string),
                           trusted=[False] + self.trusted + [False])

    def __int__(self, *args, **kwargs):
        return int(self.string, *args, **kwargs)

    # TODO: maybe return a safe_bytestring later
    def encode(self, *args, **kwargs):
        return self.string.encode(*args, **kwargs)

    def casefold(self):
        return safe_string(self.string.casefold(), trusted=self.trusted)

    def count(self, sub, *args, **kwargs):
        return self.string.count(sub.string, *args, **kwargs)

    def partition(self, sep):
        if isinstance(sep, safe_string):
            (before, sep_part, after) = self.string.partition(sep.string)
        else:
            (before, sep_part, after) = self.string.partition(sep)

        before_trusted = self.trusted[:len(before)]
        sep_trusted = self.trusted[len(before):len(before) + len(sep_part)]
        after_trusted = self.trusted[len(before) + len(sep_part):]
        return (
            safe_string(before, trusted=before_trusted),
            safe_string(sep_part, trusted=sep_trusted),
            safe_string(after, trusted=after_trusted)
        )

    def rpartition(self, sep):
        if isinstance(sep, safe_string):
            (before, sep_part, after) = self.string.rpartition(sep.string)
        else:
            (before, sep_part, after) = self.string.rpartition(sep)

        before_trusted = self.trusted[:len(before)]
        sep_trusted = self.trusted[len(before):len(before) + len(sep_part)]
        after_trusted = self.trusted[len(before) + len(sep_part):]
        return (
            safe_string(before, trusted=before_trusted),
            safe_string(sep_part, trusted=sep_trusted),
            safe_string(after, trusted=after_trusted)
        )

    def format(self, *args, **kwargs):
        return safe_format(self, *args, **kwargs)

    def format_map(self, mapping):
        return self.format(**mapping)


def dbg_safestring(string):
    return safe_string(string, [True, False] * (len(string) // 2) + [True] * (len(string) % 2))


def dbg_print_safestring(safestring):
    print(safestring.string)
    for elem in safestring.trusted:
        if elem is True:
            print('.', end='')
        else:
            print('x', end='')
    print()


if __name__ == "__main__":
    def replace_test(haystack, *args, **kwargs):
        s = safe_string(haystack, trusted=[True for _ in haystack])
        replaced = s.replace(safe_string("bar"), 
                    safe_string("ABCDEF", trusted=[True, False, True, False, True, False]), 
                    *args, **kwargs)
        print(replaced.string)
        print("".join(str(int(trust)) for trust in replaced.trusted))

    print('------- TESTING: safe string str.replace ----')
    replace_test("foobarblahbarbaz")
    replace_test("foobarblahbarbaz", count=1)
    replace_test("foobarblahbar")
    replace_test("foobarblahbar", count=1)
    replace_test("foobarblahbar", count=5)
    replace_test("fooblah", count=5)

    def title_test(haystack, *args, **kwargs):
        s = safe_string(haystack, trusted=[True for _ in haystack])
        titled = s.title()
        print(titled.string)
        print("".join(str(int(trust)) for trust in titled.trusted))

    print('------- TESTING: safe string str.title ----')
    title_test("needle")
    title_test("nEeDlE")
    title_test("NEEDLE")

    def index_test(haystack, needle):
        h = safe_string(haystack, trusted=[True for _ in haystack])
        n = safe_string(needle, trusted=[True for _ in needle])
        print(h.index(n))

    print('------- TESTING: safe string str.index ----')
    index_test("needle in a haystack", "needle")

    def rjust_test(haystack, width, c):
        h = safe_string(haystack, trusted=[True for _ in haystack])
        print(h.rjust(width).trusted)
        print(h.rjust(width, c).string)

    print('------- TESTING: safe string str.rjust ----')
    rjust_test("needle", 10, 'a')

    def split_test(string, *args, **kwargs):
        safestring = safe_string(string,
                                 [True, False] * (len(string) // 2) + [True] * (len(string) % 2))
        print([(elem.string, elem.trusted) for elem in safestring.split(*args,
                                                                        **kwargs)])

    print('------- TESTING: safe string str.split ----')
    split_test("happy\nbirth\nday")

    def center_test(string, trusted, width, fillchar=' '):
        safe_str = safe_string(string, trusted=trusted)
        new_safe_str = safe_str.center(width, fillchar)
        print(new_safe_str.string, len(new_safe_str.string))
        print(new_safe_str.trusted)

    print('------- TESTING: safe string str.center ----')
    center_test("tell", [True]*4, 5)
    center_test("tell", [True]*4, 3)
    center_test("tell", [True]*4, 6)
    center_test("tell", [True,False,True,False], 6)
    center_test("tell", [True,False,True,False], 7)
    center_test("tell", [True,False,True,False], 2)

    def find_test(string, sub, *args):
        safe_str = safe_string(string, trusted=len(string)*[True])
        find = safe_str.find(sub, *args)
        print(find)

    print('------- TESTING: safe string str.find ----')
    find_test("hello", 'h')
    find_test("hello", 'h', 2)
    find_test("hello", 'e', 1)
    find_test("hello", 'l', 2, 3)

    def ljust_test(string, width, fillchar=' '):
        safe_str = safe_string(string, trusted=len(string)*[True])
        ljust = safe_str.ljust(width, fillchar)
        print(ljust.string, len(ljust.string))
        print(ljust.trusted)

    print('------- TESTING: safe string str.ljust ----')
    ljust_test("hello", 2)
    ljust_test("hello", 7)
    ljust_test("hello", 8, 'f')

    def rfind_test(string, sub, *args):
        safe_str = safe_string(string, trusted=len(string)*[True])
        rfind = safe_str.rfind(sub, *args)
        print(rfind)

    print('------- TESTING: safe string str.rfind ----')
    rfind_test("hello", 'l', 2, 4)

    def rstrip_test(string, chars=" "):
        safe_str = safe_string(string, trusted=len(string)*[True])
        rstrip = safe_str.rstrip(chars)
        print(rstrip.string, len(rstrip.string))
        print(rstrip.trusted)

    print('------- TESTING: safe string str.rstrip ----')
    rstrip_test("hello   ")
    rstrip_test("hello   ", "o")
    rstrip_test("hello", "o")
    rstrip_test("hell", "o")

    def strip_test(string, chars=None):
        safe_str = dbg_safestring(string)
        strip = safe_str.strip(chars)
        print(strip.string, len(strip.string))
        print(strip.trusted)

    print('------- TESTING: safe string str.strip ----')
    strip_test("hello   ")
    strip_test("   he  llo   ")
    strip_test("hello   ", "o")
    strip_test("hell", "o")

    def rsplit_test(string, *args, **kwargs):
        safestring = safe_string(string,
                                 [True, False] * (len(string) // 2) + [True] * (len(string) % 2))
        print([(elem.string, elem.trusted) for elem in safestring.rsplit(*args,
                                                                         **kwargs)])

    print('------- TESTING: safe string str.rsplit ----')
    rsplit_test("abc def")
    rsplit_test("abc  def")
    rsplit_test(" abc  def")
    rsplit_test(" abc  \ndef\ndklfjd\ndd\n\n\ndlls\tfoo\t\n sls\n")
    rsplit_test(" abc  \ndef\ndklfjd\ndd\n\n\ndlls\tfoo\t\n sls\n", maxsplit=4)
    rsplit_test("-abc--d-ef-", sep="-")
    rsplit_test("-abc--d-ef-", sep="-", maxsplit=3)
    rsplit_test("-abc--d-ef-", sep="--")
    rsplit_test("-abc--d-ef-", sep="--", maxsplit=3)

    def lstrip_test(string, chars=" "):
        safe_str = safe_string(string, trusted=(len(string) // 2)*[True, False]
                               + [True] * (len(string) % 2))
        strip = safe_str.lstrip(chars)
        print(strip.string, len(strip.string))
        print(strip.trusted)

    print('------- TESTING: safe string str.lstrip ----')
    lstrip_test("hello   ")
    lstrip_test("   he  llo   ")
    lstrip_test("  he  llo   ")
    lstrip_test("hello   ", "o")
    lstrip_test("hell", "o")

    def join_test(string, seq=None):
        safe_str = dbg_safestring(string)
        if seq is None:
            seq = (safe_str.upper(), safe_str.upper())
        result = safe_str.join(seq)
        dbg_print_safestring(result)
        print(result.string)
        print(result.trusted)

    print('------- TESTING: safe string str.join ----')
    join_test("lala")
    join_test(string = "-", seq = (str(x) for x in range(1, 20)))
    join_test(string = "-", seq = {str(x): x for x in range(1, 20)})
    join_test(string = "-", seq = [str(x) for x in range(1, 20)])
    join_test(string = "-=", seq = (str(x) for x in range(1, 20)))
    join_test(string = "-=", seq = {str(x): x for x in range(1, 20)})
    join_test(string = "-=", seq = [str(x) for x in range(1, 20)])
    join_test(string = "-=", seq = (dbg_safestring("xyz"),
                                    dbg_safestring("foo"),
                                    dbg_safestring("blah")))
