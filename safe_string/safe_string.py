from bitarray import frozenbitarray


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
        raise NotImplementedError()

    def __getitem__(self, key):
        return safe_string(super().__getitem__(key), trusted=self._trusted[key])

    def __iter__(self):
        for char, trust_bit in zip(super().__iter__(), self._trusted):
            yield safe_string(char, trust_bit)

    def __add__(self, other):
        raise NotImplementedError()

    def __mul__(self, num):
        raise NotImplementedError()

    def __rmul__(self, num):
        raise NotImplementedError()

    def lstrip(self, chars=None):
        raise NotImplementedError()

    def rstrip(self, chars=None):
        raise NotImplementedError()

    def ljust(self, width, fillchar=" "):
        raise NotImplementedError()

    def rjust(self, width, fillchar=" "):
        raise NotImplementedError()

    def center(self, width, fillchar=" "):
        raise NotImplementedError()

    def zfill(self, width):
        raise NotImplementedError()

    def expandtabs(self, tabsize=8):
        raise NotImplementedError()

    def splitlines(self, keepends=False):
        raise NotImplementedError()

    def split(self, sep=None, maxsplit=-1):
        raise NotImplementedError()

    def rsplit(self, sep=None, maxsplit=-1):
        raise NotImplementedError()

    def join(self, seq):
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
        raise NotImplementedError()

    def capitalize(self):
        raise NotImplementedError()

    def casefold(self):
        raise NotImplementedError()

    def upper(self):
        raise NotImplementedError()

    def lower(self):
        raise NotImplementedError()
