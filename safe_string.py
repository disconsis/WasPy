import math

class safe_string:
    def __init__(self, string, trusted=None):
        self.string = string
        self.trusted = (
            trusted if trusted is not None 
            else [False for _ in self.string]
        )
        
    def __lt__(self, other):
        return self.string.__lt__(other.string)

    def __eq__(self, other):
        return self.string.__eq__(other.string)

    def __ge__(self, other):
        return self.string.__ge__(other.string)

    def __contains__(self, subs):
        return self.string.__contains__(subs.string)

    def title(self):
        return safe_string(
            self.string.title(), 
            trusted=self.trusted )
        
    def isascii(self):
        return self.string.isascii()

    def istitle(self):
        return self.string.istitle()
    
    def isdigit(self):
        return self.string.isdigit()

    def isalnum(self):
        return self.string.isalnum()

    def index(self, subs):
        return self.string.index(subs.string)

    def expandtabs(self, tabsize = 8):
        string = ""
        trusted = []
        for i in range(len(self.string)):
            if self.string[i] == '\t':
                string += " " * tabsize
                trusted += [self.trusted[i]] * tabsize
            else:
                string += self.string[i]
                trusted += [trusted[i]] 
        return safe_string(
            string, 
            trusted=trusted )

    def lstrip(self, chars=' '):
        string = self.string.lstrip(chars=chars)
        return safe_string(
            string, 
            trusted=self.trusted[-len(string):])

    def rjust(self, width, fillchar=' '):
        string = self.string.rjust(width, fillchar)
        trusted = self.trusted if ((len(string)-len(self.string)) <= 0) else [False]*(len(string)-len(self.string)) + self.trusted
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
                safe_string_list += [self[start:i+1]] if keepends else [self[start:i]]
                start = i+1
                
        safe_string_list += [self[start:]]
        return safe_string_list

    def endswith(self, suffix, start=0, end=math.inf):
        end = min(end, len(suffix))
        return self.string.endswith(suffix, start, end)

    def __getitem__(self, key):
        if isinstance(key, int):
            return safe_string(self.string[key], trusted=[self.trusted[key]])
        elif isinstance(key, slice):
            return safe_string(self.string[key], trusted=self.trusted[key])
        else:
            raise TypeError("Invalid indexing")

    def __iter__(self):
        return self.string.__iter__()
    
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

if __name__ == "__main__":
    def test(haystack, *args, **kwargs):
        s = safe_string(haystack, trusted=[True for _ in haystack])
        replaced = s.replace(safe_string("bar"), safe_string("ABCDEF"), *args, **kwargs)
        print(replaced.string)
        print("".join(str(int(trust)) for trust in replaced.trusted))

    test("foobarblahbarbaz")
    test("foobarblahbarbaz", count=1)
    test("foobarblahbar")
    test("foobarblahbar", count=1)
    test("foobarblahbar", count=5)
    test("fooblah", count=5)

    print()
    print()
    print()
    print()

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
 

    test2("foobarblahbarbaz")
    test2("foobarblahbarbaz", count=1)
    test2("foobarblahbar")
    test2("foobarblahbar", count=1)
    test2("foobarblahbar", count=5)
    test2("fooblah", count=5)
    test3("fooblah", count=5)
    test4("needle in a haystack", "needle")
    test5("needle", 10, 'a')
    test6("happy\nbirth\nday")