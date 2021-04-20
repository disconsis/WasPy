from bitarray import frozenbitarray


class safe_string(str):
    """
    A string which tracks trust values of each character.
    """

    # Need to overload __new__ to not pass trusted to super().__new__.
    # Use frozenbitarray instead of bitarray since it is immutable,
    # similar to str. This should prevent sharing errors.
    def __new__(cls, value, trusted: frozenbitarray):
        self = super().__new__(cls, value)
        # keep as a private attribute
        self.__trusted = trusted
        return self

    @classmethod
    def __new_untrusted(string):
        """
        Convenience method to create completely untrusted safe_string.
        """
        return safe_string(string, trusted=frozenbitarray([False] * len(string)))

    @classmethod
    def __new_trusted(string):
        """
        Convenience method to create completely trusted safe_string.
        """
        return safe_string(string, trusted=frozenbitarray([True] * len(string)))

    def __str__(self):
        # sharing should not be a problem
        # since all attributes are immutable
        return self

    def __repr__(self):
        raise NotImplementedError()

    def __getitem__(self, key):
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

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

    def format(self, *args, **kwargs):
        raise NotImplementedError()

    def format_map(self, *args, **kwargs):
        raise NotImplementedError()
