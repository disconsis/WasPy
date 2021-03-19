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

    def test2(haystack, *args, **kwargs):
        s = safe_string(haystack, trusted=[True for _ in haystack])
        replaced = s.replace(safe_string("bar"), safe_string("ABCDEF", 
            trusted=[True, False, True, False, True, False]
        ), *args, **kwargs)
        print(replaced.string)
        print("".join(str(int(trust)) for trust in replaced.trusted))

    test2("foobarblahbarbaz")
    test2("foobarblahbarbaz", count=1)
    test2("foobarblahbar")
    test2("foobarblahbar", count=1)
    test2("foobarblahbar", count=5)
    test2("fooblah", count=5)