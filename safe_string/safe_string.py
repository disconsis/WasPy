from bitarray import bitarray, frozenbitarray


class safe_string(str):
    """
    A string which tracks trust values of each character.
    """

    # Need to overload __new__ to not pass trusted to super().__new__.
    # Use frozenbitarray instead of bitarray since it is immutable,
    # similar to str. This should prevent sharing errors.
    def __new__(cls, value, trusted):
        return super().__new__(cls, value)

    def __init__(self, _string, trusted: frozenbitarray):
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
        return print(self._to_unsafe_str() + "\n" + self._trusted.to01())

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
        string = super().__add__(other)
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
        # zfill seems to behave exactly the same as rjust with fillchar="0".
        # I've tested this with some examples, and it seems to hold. The docs
        # don't suggest any special nuances either.
        # Our previous implementation just had the rjust logic for calculating
        # trusted; so even if this is wrong it's not any *more* wrong than before :P
        return self.rjust(width, "0")

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
            start_idx += dist + len(token)
            oldtoken = token

        final_trusted = frozenbitarray(final_trusted)

        return safe_string(string, final_trusted)

    def splitlines(self, keepends=False):
        raise NotImplementedError()

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

    def join(self, iterable):
        raise NotImplementedError()

    def partition(self, sep):
        raise NotImplementedError()

    def rpartition(self, sep):
        raise NotImplementedError()

    def replace(self, old, new, count=-1):
        raise NotImplementedError()

    def __format__(self, format_spec):
        raise NotImplementedError()

    def format(self, *args, **kwargs):
        raise NotImplementedError()

    def format_map(self, *args, **kwargs):
        raise NotImplementedError()

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
