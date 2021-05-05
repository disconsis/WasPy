from bitarray import bitarray, frozenbitarray
from forbiddenfruit import curse
import itertools

orig_str_add = str.__add__
orig_str_format = str.format

def safe_format(fmt_string, *args, **kwargs):
    result_string = orig_str_format(fmt_string, *args, **kwargs)
    arg_holes, all_holes = _do_build_string(fmt_string)
    arg_hole_trusts = render_field(arg_holes, fmt_string, args, kwargs)
    final_trusted = construct_trusted(fmt_string, all_holes, arg_hole_trusts)
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
            s = value._to_unsafe_str()

        if conv == 'r':
            trusted = bitarray(value.__repr__()._trusted) if is_safe else bitarray([
                False]*len(repr(s).__format__(spec._to_unsafe_str())))
            result.append(trusted)
        elif conv == 's':
            trusted = bitarray(value.__str__()._trusted) if is_safe else bitarray([
                False]*len(str(s).__format__(spec._to_unsafe_str())))
            result.append(trusted)
        elif conv == 'a':
            if not is_safe:
                trusted = bitarray([False] * len(ascii(value)))
            elif value.isascii():
                trusted = bitarray([False]) + value._trusted + bitarray([False])
            else:
                # go char-by-char and call ascii
                trusted = bitarray()
                for char in value:
                    newchar = ascii(char._to_unsafe_str())[1:-1]  # remove quotes
                    trusted += len(newchar) * char._trusted
                trusted = bitarray([False]) + trusted + bitarray([False])  # for quotes

            result.append(trusted)
        else:
            trusted = bitarray(value._trusted) if is_safe else bitarray([
                False]*len(s.__format__(spec._to_unsafe_str())))
            result.append(trusted)

    return result


def construct_trusted(format_string, gl_holes, trusted_result):
    prev_index = 0
    gl_index = 0
    hl_index = 0
    final_trusted = bitarray()
    while gl_index < len(gl_holes):
        start = gl_holes[gl_index][1][0]
        end = gl_holes[gl_index][1][1]
        final_trusted += format_string._trusted[prev_index:start]
        new_trusted = bitarray()
        if gl_holes[gl_index][0] == 'l' or gl_holes[gl_index][0] == 'r':
            new_trusted += [format_string._trusted[end]]
        else:
            new_trusted += trusted_result[hl_index]
            hl_index += 1
        final_trusted += new_trusted
        gl_index += 1
        prev_index = end+1

    final_trusted += format_string._trusted[prev_index:]

    return final_trusted


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


class safe_string(str):
    """
    A string which tracks trust values of each character.
    """

    # Need to overload __new__ to not pass trusted to super().__new__.
    # Use frozenbitarray instead of bitarray since it is immutable,
    # similar to str. This should prevent sharing errors.
    # TODO: have a default trusted generator
    def __new__(cls, value, trusted=None):
        return super().__new__(cls, value)

    # TODO: Add raise error if trusted and string are of different lengths
    def __init__(self, _string, trusted: frozenbitarray = None):
        if trusted is None:
            trusted = frozenbitarray([False]*len(_string))
        super().__init__()
        # keep as a private attribute
        self._trusted = trusted

    @staticmethod
    def _new_untrusted(string):
        """
        Convenience method to create completely untrusted safe_string.
        """
        return safe_string(string, trusted=frozenbitarray([False] * len(string)))

    @staticmethod
    def _new_trusted(string):
        """
        Convenience method to create completely trusted safe_string.
        """
        return safe_string(string, trusted=frozenbitarray([True] * len(string)))

    def _to_unsafe_str(self):
        "Convert back to a simple str."
        return super().__str__()

    def _debug_repr(self):
        "Debugging: print a representation which shows the trust values of each char."
        return print(orig_str_add(orig_str_add(self._to_unsafe_str(), "\n"),
                                  self._trusted.to01()))

    def __str__(self):
        # sharing should not be a problem
        # since all attributes are immutable
        return self

    def __repr__(self):
        """
        __repr__ override for safe_string objects.

        `str.__repr__` has a complicated escaping logic. It escapes backslashes, special
        escape characters (\n, \t, ...) but also unicode codepoints outside the printable
        range.
        There might be more to it. For now, a slow but safe approach is to use the trusted
        value of each character as the trusted of its repr, and concat them together.

        Examples:
          repr("\\") == "'\\\\'"
          repr("\n") == "'\\n'"
          repr("\x0c") == "'\\x0c'"
          repr("\x1c") == "'\\x1c'"
          repr("\x2c") == "','" == "'\x2c'"

          repr("'") == "'"
          repr('"') == '"'
          repr("'\"") == '\'"'
        """

        # XXX uncomment for debugging
        # return "\n" + repr(self._to_unsafe_str()) + "\n" + repr(self._trusted.to01())

        repr_string = super().__repr__()
        if len(repr_string) - len(self) == 2:
            # nothing has been escaped; only quotes have been added
            # TODO: should these quotes be trusted? since this is performed by the developer
            repr_trusted = frozenbitarray([False]) + self._trusted + frozenbitarray([False])
        else:
            # some characters have been escaped
            # we have no way to know which without looping through the string

            repr_trusted = bitarray([False])

            # single quote is only escaped if the repr string
            # is surrounded with single quotes, but this doesn't
            # show up if you call repr on it by itself (since it wraps
            # it in double quotes).
            single_quote_escaped = (repr_string[0] == "'")

            for char in self:
                if char == "'" and single_quote_escaped:
                    len_repr = 2
                else:
                    len_repr = len(str.__repr__(char)) - 2

                repr_trusted.extend(char._trusted * len_repr)

            repr_trusted.append(False)

            # freeze to make immutable
            repr_trusted = frozenbitarray(repr_trusted)

        return safe_string(repr_string, repr_trusted)

    def __getitem__(self, key):
        # call str method first to get same behaviour on error
        new_string = super().__getitem__(key)

        if isinstance(key, int):
            new_trusted = self._trusted[key:key + 1]
        elif isinstance(key, slice):
            new_trusted = self._trusted[key]
        else:
            raise TypeError("indices must be integers or slices")

        return safe_string(new_string, new_trusted)

    def __iter__(self):
        for char, trust_bit in zip(super().__iter__(), self._trusted):
            yield safe_string(char, frozenbitarray([trust_bit]))

    def __add__(self, other):
        # call str method first to get same behaviour on error
        string = orig_str_add(self, other)
        if isinstance(other, safe_string):
            trusted = self._trusted + other._trusted
            return safe_string(string, trusted)
        elif isinstance(other, str):
            trusted = self._trusted + (frozenbitarray([False] * len(other)))
            return safe_string(string, trusted)
        else:
            raise TypeError("argument must be a str or safe_string")

    def __mul__(self, num):
        return safe_string(
            super().__mul__(num),
            self._trusted * num
        )

    def __rmul__(self, num):
        return self.__mul__(num)

    def lstrip(self, chars=None):
        string = super().lstrip(chars)
        return safe_string(string, self._trusted[-len(string):])

    def rstrip(self, chars=None):
        string = super().rstrip(chars)
        return safe_string(string, self._trusted[:len(string)])

    def strip(self, chars=None):
        return self.lstrip(chars).rstrip(chars)

    def ljust(self, width, fillchar=" "):
        string = super().ljust(width, fillchar)

        if isinstance(fillchar, safe_string):
            fillchar_trust = fillchar._trusted[0]
        else:
            fillchar_trust = False

        trusted = self._trusted + max(0, width - len(self)) * frozenbitarray([fillchar_trust])
        return safe_string(string, trusted)

    def rjust(self, width, fillchar=" "):
        string = super().rjust(width, fillchar)

        if isinstance(fillchar, safe_string):
            fillchar_trust = fillchar._trusted[0]
        else:
            fillchar_trust = False

        trusted = max(0, width - len(self)) * frozenbitarray([fillchar_trust]) + self._trusted
        return safe_string(string, trusted)

    def center(self, width, fillchar=" "):
        string = super().center(width, fillchar)

        if isinstance(fillchar, safe_string):
            fillchar_trust = fillchar._trusted[0]
        else:
            fillchar_trust = False

        fillchar_trusted = frozenbitarray([fillchar_trust])

        marg = width - len(self)
        left_fill = (marg // 2 + (marg & width & 1)) * fillchar_trusted
        right_fill = (marg - len(left_fill)) * fillchar_trusted
        trusted = left_fill + self._trusted + right_fill

        return safe_string(string, trusted)

    def zfill(self, width):
        # zfill has special behaviour if the string starts with +/-
        string = super().zfill(width)
        if not string:
            return self

        num_extra = len(string) - len(self)
        if string[0] == self[0]:
            trusted = self._trusted[0:1] + frozenbitarray([False]) * num_extra + self._trusted[1:]
        else:
            trusted = frozenbitarray([False]) * num_extra + self._trusted

        return safe_string(string, trusted)

    @staticmethod
    def _tabindent(token, tabsize):
        """
        Calculates distance behind the token to the next tabstop.
        Taken almost verbatim from pypy3.6.
        """

        if tabsize <= 0:
            return 0
        distance = tabsize
        if token:
            distance = 0
            offset = len(token)

            while 1:
                if token[offset-1] == "\n" or token[offset-1] == "\r":
                    break
                distance += 1
                offset -= 1
                if offset == 0:
                    break

            # the same like distance = len(token) - (offset + 1)
            distance = (tabsize - distance) % tabsize
            if distance == 0:
                distance = tabsize

        return distance

    def expandtabs(self, tabsize=8):
        """
        Override for expandtabs. This function is a lot more complicated than
        our initial assumption - we thought it would just expand each "\t" to
        tabsize " " characters. This turns out to be completely false.
        The function does a much more useful job of aligning the segment following
        a "\t" to the next tabstop. The calculation for this is somewhat nuanced,
        and is mostly derived from pypy3.6's implementation.
        """
        if not self:
            return self

        string = super().expandtabs(tabsize)
        splitted = self.split("\t")
        # keep track of idx to get trust value of \t
        oldtoken = splitted.pop(0)
        final_trusted = bitarray(oldtoken._trusted)
        start_idx = len(final_trusted)
        for token in splitted:
            dist = self._tabindent(oldtoken, tabsize)
            final_trusted.extend(self._trusted[start_idx:start_idx + 1] * dist)
            final_trusted.extend(token._trusted)
            start_idx += 1 + len(token)
            oldtoken = token

        final_trusted = frozenbitarray(final_trusted)

        return safe_string(string, final_trusted)

    def splitlines(self, keepends=False):

        line_boundaries = ['\n', '\r', '\r\n', '\v', '\x0b', '\f', '\x0c', '\x1c', 
                            '\x1d', '\x1e', '\x85', '\u2028', '\u2029']
        
        safe_string_list = []
        start = 0
        i = 0
        while i < len(self):
            if self[i] in line_boundaries:
                start_idx = start
                end_idx = i+1 if keepends else i
                if i+1 < len(self) and self[i] == '\r' and self[i+1] == '\n':
                    if keepends:
                        end_idx += 1
                    safe_string_list.append(self[start_idx:end_idx])
                    i += 1
                else:
                    safe_string_list.append(self[start_idx:end_idx])
                start = i+1
            i += 1

        if start < len(self):
            safe_string_list.append(self[start:])
        return safe_string_list

    def split(self, sep=None, maxsplit=-1):
        str_splits = super().split(sep, maxsplit)

        result = []
        # we start counting from the start because irrespective of
        # the value of `maxsplit`, if sep=None and the string starts with
        # whitespace, then the whitespace is removed from the start
        start_idx = 0
        if sep is None:
            while start_idx < len(self) \
                  and str.isspace(str.__getitem__(self, start_idx)):
                start_idx += 1

        for elem in str_splits:
            elem_trusted = self._trusted[start_idx:start_idx + len(elem)]
            result.append(safe_string(elem, elem_trusted))

            start_idx += len(elem)
            if sep is None:
                while start_idx < len(self) \
                        and str.isspace(str.__getitem__(self, start_idx)):
                    start_idx += 1
            else:
                start_idx += len(sep)
        return result

    def rsplit(self, sep=None, maxsplit=-1):
        str_splits = super().rsplit(sep, maxsplit)

        result = []
        # we start counting from the end because irrespective of
        # the value of `maxsplit`, if sep=None and the string ends with
        # whitespace, then the whitespace is removed from the end
        end_idx = len(self) - 1
        if sep is None:
            while end_idx >= 0 \
                  and str.isspace(str.__getitem__(self, end_idx)):
                end_idx -= 1

        for elem in reversed(str_splits):
            elem_trusted = self._trusted[end_idx - len(elem) + 1:end_idx + 1]
            result.append(safe_string(elem, elem_trusted))

            end_idx -= len(elem)
            if sep is None:
                while end_idx >= 0 \
                        and str.isspace(str.__getitem__(self, end_idx)):
                    end_idx -= 1
            else:
                end_idx -= len(sep)

        result.reverse()
        return result

    # TODO: Find better way to compute join of trusted. List comprehension does not work.
    def join(self, iterable):

        seq = iter(iterable)

        try:
            first_elem = next(seq)
            final = first_elem
        except StopIteration:
            return safe_string("", trusted=frozenbitarray())

        for elem in seq:
            final += self + elem

        return final

    def partition(self, sep):
        (before, sep_part, after) = super().partition(sep)
        before_trusted = self._trusted[:len(before)]
        sep_trusted = self._trusted[len(before): len(before) + len(sep_part)]
        after_trusted = self._trusted[len(before) + len(sep_part):]
        return (
            safe_string(before, trusted=before_trusted),
            safe_string(sep_part, trusted=sep_trusted),
            safe_string(after, after_trusted)
        )

    def rpartition(self, sep):
        (before, sep_part, after) = super().rpartition(sep)
        before_trusted = self._trusted[:len(before)]
        sep_trusted = self._trusted[len(before): len(before) + len(sep_part)]
        after_trusted = self._trusted[len(before) + len(sep_part):]
        return (
            safe_string(before, trusted=before_trusted),
            safe_string(sep_part, trusted=sep_trusted),
            safe_string(after, after_trusted)
        )

    def replace(self, old, new, count=-1):
        count = super().count(old) if count == -1 else min(count, super().count(old))
        result_string = super().replace(old, new, count)
        result_trusted = bitarray()
        start_idx = 0
        while count > 0:
            idx = self.find(old, start_idx)
            if idx == -1:
                break
            else:
                result_trusted.extend(self._trusted[start_idx:idx])
                result_trusted.extend(new._trusted)
                start_idx = idx + len(old)
                count -= 1

        result_trusted.extend(self._trusted[start_idx:])

        return safe_string(result_string, frozenbitarray(result_trusted))

    # XXX comment for debugging
    def __format__(self, format_spec):
        return str.__format__(self._to_unsafe_str(), format_spec)

    def format(self, *args, **kwargs):
        return safe_format(self, *args, **kwargs)

    def format_map(self, kwargs):
        return self.format(**kwargs)

    def title(self):
        return safe_string(
            super().title(),
            self._trusted
        )

    def capitalize(self):
        return safe_string(
            super().capitalize(),
            self._trusted
        )

    def casefold(self):
        return safe_string(
            super().casefold(),
            self._trusted
        )

    def upper(self):
        return safe_string(
            super().upper(),
            self._trusted
        )

    def lower(self):
        return safe_string(
            super().lower(),
            self._trusted
        )

    def swapcase(self):
        return safe_string(
            super().swapcase(),
            self._trusted
        )


def new_str_add(str1, str2):
    if isinstance(str2, safe_string):
        str1 = safe_string._new_untrusted(str1)
        return str1 + str2
    else:
        return orig_str_add(str1, str2)


def new_str_format(fmt_string, *args, **kwargs):
    is_safe_string = False
    for arg in itertools.chain(args, kwargs.values()):
        if isinstance(arg, safe_string):
            is_safe_string = True
            break

    if not is_safe_string:
        return orig_str_format(fmt_string, *args, **kwargs)
    else:
        return safe_string._new_untrusted(fmt_string).format(
            *args, **kwargs)


curse(str, "__add__", new_str_add)
curse(str, "format", new_str_format)


def trusted_string(string):
    return safe_string._new_trusted(string)
