import math

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
        trusted = self.trusted if ((len(string)-len(self.string)) <= 0) else [char_trust]*(len(string)-len(self.string)) + self.trusted
        return safe_string(
            string,
            trusted=trusted)

    def zfill(self, width):
        string = self.string.zfill(width)
        trusted = self.trusted if ((len(string)-len(self.string)) <= 0) else [False]*(len(string)-len(self.string)) + self.trusted
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
        if isinstance(key, int):
            return safe_string(self.string[key], trusted=[self.trusted[key]])
        elif isinstance(key, slice):
            return safe_string(self.string[key], trusted=self.trusted[key])
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
        seq_str = []
        for s in seq:
            seq_str += [s.string]

        str_join = self.string.join(seq_str)
        trusted = []
        i = 0
        print(seq_str)
        for s in seq:
            if(i == len(seq)-1):
                trusted += s.trusted 
            else:   
                trusted += (s.trusted + self.trusted)
            i += 1
        return safe_string(str_join ,trusted = trusted)


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


if __name__ == "__main__":
    def test(haystack, *args, **kwargs):
        s = safe_string(haystack, trusted=[True for _ in haystack])
        replaced = s.replace(safe_string("bar"), safe_string("ABCDEF"), *args, **kwargs)
        print(replaced.string)
        print("".join(str(int(trust)) for trust in replaced.trusted))

    # test("foobarblahbarbaz")
    # test("foobarblahbarbaz", count=1)
    # test("foobarblahbar")
    # test("foobarblahbar", count=1)
    # test("foobarblahbar", count=5)
    # test("fooblah", count=5)

    # print()
    # print()
    # print()
    # print()

    def test3(haystack, *args, **kwargs):
        s = safe_string(haystack, trusted=[True for _ in haystack])
        titled = s.title()
        print(titled.string)
        # print("".join(str(int(trust)) for trust in replaced.trusted))
    def test4(haystack, needle):
        h = safe_string(haystack, trusted=[True for _ in haystack])
        n = safe_string(needle, trusted=[True for _ in needle])
        print(h.index(n))
    
    def test5(haystack, width, c):
        h = safe_string(haystack, trusted=[True for _ in haystack])
        print(h.rjust(width).trusted)
        print(h.rjust(width,c).string)

    def test2(haystack, *args, **kwargs):
        s = safe_string(haystack, trusted=[True for _ in haystack])
        replaced = s.replace(safe_string("bar"), safe_string("ABCDEF", 
            trusted=[True, False, True, False, True, False]
        ), *args, **kwargs)
        print(replaced.string)
        print("".join(str(int(trust)) for trust in replaced.trusted))
    
    def test6(haystack):
        s = safe_string(haystack, trusted=[True for _ in haystack])
        lines = s.splitlines(True)
        [print(l.string) for l in lines]
 

    # test2("foobarblahbarbaz")
    # test2("foobarblahbarbaz", count=1)
    # test2("foobarblahbar")
    # test2("foobarblahbar", count=1)
    # test2("foobarblahbar", count=5)
    # test2("fooblah", count=5)
    # test3("fooblah", count=5)
    # test4("needle in a haystack", "needle")
    # test5("needle", 10, 'a')
    # test6("happy\nbirth\nday")

    def center_test(string, trusted, width, fillchar=' '):
        safe_str = safe_string(string, trusted=trusted)
        new_safe_str = safe_str.center(width, fillchar)
        print(new_safe_str.string, len(new_safe_str.string))
        print(new_safe_str.trusted)

    # center_test("tell", [True]*4, 5)
    # center_test("tell", [True]*4, 3)
    # center_test("tell", [True]*4, 6)
    # center_test("tell", [True,False,True,False], 6)
    # center_test("tell", [True,False,True,False], 7)
    # center_test("tell", [True,False,True,False], 2)

    def find_test(string, sub, *args):
        safe_str = safe_string(string, trusted=len(string)*[True])
        find = safe_str.find(sub, *args)
        print(find)

    # find_test("hello", 'h')
    # find_test("hello", 'h', 2)
    # find_test("hello", 'e', 1)
    # find_test("hello", 'l', 2, 3)

    def ljust_test(string, width, fillchar=' '):
        safe_str = safe_string(string, trusted=len(string)*[True])
        ljust = safe_str.ljust(width, fillchar)
        print(ljust.string, len(ljust.string))
        print(ljust.trusted)

    # ljust_test("hello", 2)
    # ljust_test("hello", 7)
    # ljust_test("hello", 8, 'f')

    def rfind_test(string, sub, *args):
        safe_str = safe_string(string, trusted=len(string)*[True])
        rfind = safe_str.rfind(sub, *args)
        print(rfind)

    # rfind_test("hello", 'l', 2, 4)

    def rstrip_test(string, chars=" "):
        safe_str = safe_string(string, trusted=len(string)*[True])
        rstrip = safe_str.rstrip(chars)
        print(rstrip.string, len(rstrip.string))
        print(rstrip.trusted)

    # rstrip_test("hello   ")
    # rstrip_test("hello   ", "o")
    # rstrip_test("hello", "o")
    # rstrip_test("hell", "o")

    def dbg_safestring(string):
        return safe_string(string, [True, False] * (len(string) // 2) + [True] * (len(string) % 2))


    def strip_test(string, chars=None):
        safe_str = dbg_safestring(string)
        strip = safe_str.strip(chars)
        print(strip.string, len(strip.string))
        print(strip.trusted)

    # strip_test("hello   ")
    # strip_test("   he  llo   ")
    # strip_test("hello   ", "o")
    # strip_test("hell", "o")

    def rsplit_test(string, *args, **kwargs):
        actual = [elem.string
                  for elem in safe_string(string).rsplit(*args, **kwargs)]
        expected = string.rsplit(*args, **kwargs)
        if actual == expected:
            print('.')
        else:
            print('!', "actual:", actual, "expected:", expected)

    # rsplit_test("abc def")
    # rsplit_test("abc  def")
    # rsplit_test(" abc  def")
    # rsplit_test(" abc  \ndef\ndklfjd\ndd\n\n\ndlls\tfoo\t\n sls\n")
    # rsplit_test(" abc  \ndef\ndklfjd\ndd\n\n\ndlls\tfoo\t\n sls\n", maxsplit=4)
    # rsplit_test("-abc--d-ef-", sep="-")
    # rsplit_test("-abc--d-ef-", sep="-", maxsplit=3)
    # rsplit_test("-abc--d-ef-", sep="--")
    # rsplit_test("-abc--d-ef-", sep="--", maxsplit=3)

    def lstrip_test(string, chars=" "):
        safe_str = safe_string(string, trusted=(len(string) // 2)*[True, False]
                               + [True] * (len(string) % 2))
        strip = safe_str.lstrip(chars)
        print(strip.string, len(strip.string))
        print(strip.trusted)

    # lstrip_test("hello   ")
    # lstrip_test("   he  llo   ")
    # lstrip_test("  he  llo   ")
    # lstrip_test("hello   ", "o")
    # lstrip_test("hell", "o")

    def split_test(string, *args, **kwargs):
        safestring = safe_string(string,
                                 [True, False] * (len(string) // 2) + [True] * (len(string) % 2))
        print([(elem.string, elem.trusted) for elem in safestring.split(*args,
                                                                        **kwargs)])

    def rsplit_test(string, *args, **kwargs):
        safestring = safe_string(string,
                                 [True, False] * (len(string) // 2) + [True] * (len(string) % 2))
        print([(elem.string, elem.trusted) for elem in safestring.rsplit(*args,
                                                                         **kwargs)])


    def join_test(string, seq=None):
        safe_str = dbg_safestring(string)
        seq = (safe_str.upper(), safe_str.upper())
        result = safe_str.join(seq)
        print(result.string)
        print(result.trusted)

join_test("lala")