from safe_string import safe_string, dbg_safestring, dbg_print_safestring

class OverrideUnsafe:
    def __init__(self, safe_obj):
        self.obj = safe_obj

    def __format__(self, *args, **kwargs):
        if isinstance(self.obj, safe_string):
            result = format(self.obj, *args, **kwargs)
        else:
            result = self.obj.__format__(*args, **kwargs)

        if isinstance(result, safe_string):
            return result.string
        else:
            return result

    def __repr__(self):
        result = self.obj.__repr__()
        if isinstance(result, safe_string):
            return result.string
        else:
            return result

    def __str__(self):
        result = self.obj.__str__()
        if isinstance(result, safe_string):
            return result.string
        else:
            return result

    def __getitem__(self, *args, **kwargs):
        return OverrideUnsafe(self.obj.__getitem__(*args, **kwargs))

    def __getattr__(self, *args, **kwargs):
        return OverrideUnsafe(self.obj.__getattribute__(*args, **kwargs))


def format(fmt_string, *args, **kwargs):
    if not isinstance(fmt_string, safe_string):
        fmt_string = safe_string(fmt_string)
    unsafe_args = list(map(OverrideUnsafe, args))
    unsafe_kwargs = {key: OverrideUnsafe(value)
                     for key, value in kwargs.items()}

    result_string = fmt_string.string.format(*unsafe_args, **unsafe_kwargs)
    arg_holes, all_holes = _do_build_string(fmt_string)
    arg_hole_trusts = render_field(arg_holes, fmt_string, args, kwargs)
    final_trusted = construct_trusted(fmt_string, all_holes, arg_hole_trusts)
    if len(result_string) != len(final_trusted):
        print("ERROR:")
        dbg_print_safestring(safe_string(result_string, trusted=final_trusted))
        print(
            f"str len = {len(result_string)} | trust len = {len(final_trusted)}")
        raise Exception("mismatched lengths")
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

        elif s[i] == '}':
            if isHole:
                res.append(('h', (lb_loc, i)))
                holes.append((lb_loc, i))
                isHole = False
            elif i < len(s)-1 and s[i+1] == '}':
                res.append(('r', (i, i+1)))
                i += 1
        i += 1

#     print(holes)
#     print(res)
#     print()

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
            s = value.string

        if conv == 'r':
            trusted = value.__repr__().trusted if is_safe else [
                False]*len(repr(s).__format__(spec.string))
            result.append(trusted)
        elif conv == 's':
            trusted = value.__str__().trusted if is_safe else [
                False]*len(str(s).__format__(spec.string))
            result.append(trusted)
        elif conv == 'a':
            if not is_safe:
                trusted = [False] * len(ascii(value))
            elif value.isascii():
                trusted = [False] + value.trusted + [False]
            else:
                # go char-by-char and call ascii
                trusted = []
                for char in value:
                    newchar = ascii(char.string)[1:-1] # remove quotes
                    trusted += len(newchar) * char.trusted
                trusted = [False] + trusted + [False] # for quotes

            result.append(trusted)
        else:
            trusted = value.trusted if is_safe else [
                False]*len(s.__format__(spec.string))
            result.append(trusted)

    return result


def construct_trusted(format_string, gl_holes, trusted_result):
    # print(f"trusted_result: {trusted_result}")
    # print(f"gl_holes: {gl_holes}")
    prev_index = 0
    gl_index = 0
    hl_index = 0
    final_trusted = []
    while gl_index < len(gl_holes):
        start = gl_holes[gl_index][1][0]
        end = gl_holes[gl_index][1][1]
        final_trusted += format_string.trusted[prev_index:start]
        new_trusted = []
        if gl_holes[gl_index][0] == 'l' or gl_holes[gl_index][0] == 'r':
            new_trusted += [format_string.trusted[end]]
        else:
            new_trusted += trusted_result[hl_index]
            hl_index += 1
        final_trusted += new_trusted
        gl_index += 1
        prev_index = end+1

    final_trusted += format_string.trusted[prev_index:]

    return final_trusted

    # min_start = min(lb[0])


test_cases = ["{abc}", "{{", "}}", "{{{}}}", "{}{}{}", "}", "{{{{}}}}"]
for s in test_cases:
    _do_build_string(s)


# KETAN


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


def test_parse_field():
    assert parse_field("{}") == ("", None, "")
    assert parse_field("{0}") == ("0", None, "")
    assert parse_field("{name}") == ("name", None, "")

    assert parse_field("{!r}") == ("", "r", "")
    assert parse_field("{0!s}") == ("0", "s", "")
    assert parse_field("{name!a}") == ("name", "a", "")

    assert parse_field("{[0]}") == ("[0]", None, "")
    assert parse_field("{0.blah}") == ("0.blah", None, "")
    assert parse_field("{name}") == ("name", None, "")
    assert parse_field("{.name}") == (".name", None, "")

    assert parse_field("{[0]:!foo}") == ("[0]", None, "!foo")
    assert parse_field("{0.blah:x}") == ("0.blah", None, "x")
    assert parse_field("{name:[!foo]}") == ("name", None, "[!foo]")
    assert parse_field("{.name[!foo]}") == (".name[!foo]", None, "")

    assert parse_field("{[0]!x:!foo}") == ("[0]", "x", "!foo")
    assert parse_field("{0.blah!f:x}") == ("0.blah", "f", "x")
    assert parse_field("{name!f:[!foo]}") == ("name", "f", "[!foo]")
    assert parse_field("{.name[!foo]!c}") == (".name[!foo]", "c", "")


def test_get_argument():
    get_arg = get_argument([10, 20, 30, 40], {"name": "foo"})
    assert get_arg("[0]") == 10
    assert get_arg(".foo") == 20
    assert get_arg("[0][1]") == 30
    assert get_arg("name.blah") == "foo"
    assert get_arg("3[0].blah") == 40


def test_resolve_lookups():
    assert resolve_lookups([{"name": "foo"}], "[0][name]") == "foo"

    from types import SimpleNamespace
    person = SimpleNamespace()
    person.name = "foo"
    assert resolve_lookups([{"p": person}], "[0][p].name") == "foo"

    person = SimpleNamespace()
    person.name = SimpleNamespace()
    person.name.first = "foo"
    assert resolve_lookups([{"p": person}], "[0][p].name.first") == "foo"

    person = SimpleNamespace()
    person.name = ["foo", "bar"]
    items = SimpleNamespace()
    items.first = {"p": person}
    assert resolve_lookups(items, ".first[p].name[0]") == "foo"


def test_field_parser():
    parser = field_parser([10, 20, 30, 40], {"name": "foo"})
    assert parser("{name[0]}") == ("f", None, "")
    assert parser("{}") == (10, None, "")
    assert parser("{name[0]:[1]}") == ("f", None, "[1]")


if __name__ == '__main__':
    fmt_s = "{name[0]!a} {!s} {!r}"
    fmt = safe_string(fmt_s, trusted=[True] * len(fmt_s))
    nino = b"Ni\xc3\xb10".decode("utf-8")
    dbg_print_safestring(format(fmt, 10, 18, name=[dbg_safestring(nino)]))
