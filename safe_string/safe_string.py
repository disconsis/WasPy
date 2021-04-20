class safe_string(str):
    def __str__(self):
        raise NotImplementedError()

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
