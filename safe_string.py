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

    def __ne__(self, other):
        if isinstance(other, safe_string):
            return self.string.__ne__(other.string)
        else:
            return self.string.__ne__(other)

    def __ge__(self, other):
        return self.string.__ge__(other.string)

    def __contains__(self, subs):
        return self.string.__contains__(subs.string)

    def __new__(cls, string, trusted=None):
        return super(safe_string, cls).__new__(cls)

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

    def split(self, sep, maxsplit=math.inf):
        str_splits = self.string.split(sep, min(maxsplit, len(self.string)))
        start_idx = 0
        list_splits = []
        for ele in str_splits:
            new_ele = safe_string(ele, trusted=self.trusted[start_idx:start_idx+len(ele)])
            list_splits.append(new_ele)
            start_idx += len(ele)+1
        return list_splits

    def capitalize(self):
        return safe_string(self.string.capitalize(), trusted=self.trusted)

    def center(self, width, fillchar=' '):
        new_str = self.string.center(width, fillchar)
        left_fill = int(max(0, (width-len(self.string)+1)/2))*[False]
        right_fill = int(max(0, (width-len(self.string))/2))*[False]
        new_trusted = left_fill+self.trusted+right_fill
        return safe_string(new_str, trusted=new_trusted)

    def find(self, sub, *args):
        return self.string.find(sub, *args)

    def ljust(self, width, fillchar=' '):
        new_str = self.string.ljust(width, fillchar)
        new_trusted = self.trusted + max(0, (width-len(self.string)))*[False]
        return safe_string(new_str, trusted=new_trusted)

    def rfind(self, sub, *args):
        return self.string.rfind(sub, *args)

    def rstrip(self, chars=" "):
        new_str = self.string.rstrip(chars)
        return safe_string(
            new_str, 
            trusted=self.trusted[:len(new_str)])

    def strip(self, chars=" "):
        new_str = self.string.strip(chars)
        start_idx = 0
        while start_idx < len(self.string):
            if self.string[start_idx] not in chars:
                break
            start_idx += 1
        end_idx = len(self.string)-1
        while end_idx >= 0:
            if self.string[end_idx] not in chars:
                break
            end_idx -= 1
        return safe_string(
            new_str,
            trusted=self.trusted[start_idx:end_idx+1]
        )
    
    def upper(self):
        return safe_string(self.string.upper(), trusted=self.trusted)

    def islower(self):
        return self.string.islower()

    def isspace(self):
        return self.string.isspace()

    def isidentifier(self):
        return self.string.isidentifier()

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

    def strip_test(string, chars=" "):
        safe_str = safe_string(string, trusted=len(string)*[True])
        strip = safe_str.strip(chars)
        print(strip.string, len(strip.string))
        print(strip.trusted)

    # strip_test("hello   ")
    # strip_test("   he  llo   ")
    # strip_test("hello   ", "o")
    # strip_test("hell", "o")