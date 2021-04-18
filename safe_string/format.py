from safe_string import (
    safe_string,
    dbg_safestring,
    dbg_print_safestring,
    parse_field,
    get_argument,
    resolve_lookups,
    field_parser,
)


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
