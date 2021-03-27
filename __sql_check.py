#!/usr/bin/env python3

import random
import string
import sqlparse
import IPython

"statement;\r\n\t "

fails = []
unknowns = []


def check(randstr):
    parsed = "".join(str(statement) for statement in sqlparse.parse(randstr))

    if parsed != randstr:
        fails.append(randstr)
        if randstr.startswith(parsed):
            if randstr.rstrip("\r\n") == parsed.rstrip("\r\n"):
                print("N", end="", flush=True)
            else:
                print("P", end="", flush=True)
        elif randstr.endswith(parsed):
            print("S", end="", flush=True)
        else:
            print("\nUnknown failure:", repr(randstr))
            unknowns.append(randstr)

        return True

    else:
        print('.', end='', flush=True)
        return True


for _ in range(100):
    length = random.randrange(10, 100)
    randstr = "".join(random.choices(string.printable,
                                     weights=[20 if elem.isspace() else 1
                                              for elem in string.printable], k=length))

    # parsed = "".join(str(statement) for statement in sqlparse.parse(randstr))
    same = check(randstr)
    if not same and (len(fails) > 20 or len(unknowns) >= 1):
        break


if len(fails) != 0:
    print("Fails: ", len(fails))

IPython.embed()
