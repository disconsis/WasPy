# str.format


"fmt string {field!conv:spec}".format(1, 2, 3, key="blah", num=5, obj=Person())

"   {{ }}  {f1}          {f2}       {f3}       {{blah}} {{{should}}} ".format(....)
[   ll rr  ----          ----       ----       ll    rr ll--------rr  ]

f1 : arg1
f2 : arg3
f3 : arg9

```python
def render_field(arg1, conv1, spec1):
  if conv1 == 'r':
    return repr(arg1).__format__(spec1)
  elif conv1 == 's':
    return str(arg1).__format__(spec1)
  elif conv1 == 'a':
    return ascii(arg1).__format__(spec1)
  else:
    return arg1.__format__(spec1)
```

- positional args: manual and auto-numbering cannot be mixed
- indexes are only looked for in positional args, never kwargs

## Pseudocode
1. find start, end of each field hole # use single-pass, counting { and }'s # `_do_build_string`
  - also return escaped { and } holes
2. parse field into 'field.lookup', 'conv', 'spec'
3. relate field.lookup to object from arguments # `_get_argument` (make sure to do lookup)
4. call `render_field()` on it to get length # `self._render_field` # needs testing
5. if argument is a `safe_string`, use its trusted array, otherwise use [False] * len
6. replace trusted arrays in the field holes
7. call `str.format` to get final string

## Grouping
1
2-3
4-7

## References
objspace/std/newformat.py

## TODO
- make sure ascii() works correctly on safestring
- mod: "%4d %s" % (5, "foo")

# Syntax-Aware Checking

## Pseudocode
1. call `sqlparse.parse` and `.flatten()` on the `self.string` -> list of tokens
2. for each token, figure out starting index (linear pass taking sum of lengths)
3. for each token, if `token not in sqlparse.tokens.Literal`, then make sure each character is trusted (using the starting index to index into `self.trusted`)
4. if this check fails for any character, return *SQLI detected*, Otherwise, *No SQLI*

```python
def tcheck(string):
    for statement in sqlparse.parse(string):
        print("Statement:", str(statement))
        for token in statement.flatten():
            isliteral = token.ttype in sqlparse.tokens.Literal
            print(f"Token: {token} \t\t\t type = {token.ttype} \t\t lit = {isliteral}")
```

## Notes
- Maybe quotes in string literals should also be trusted

## Testing
- Get bunch of sql query templates, attack payloads, and benign sql queries
- for template in templates:
  - for payload in attack payloads:
    - create query
    - run `has_sqli`
    - if true, then fine
    - otherwise, could be because of syntax error
    - run query against bunch of sql servers
    - if one of them doesn't mark it as a syntax error, flag as *false negative*
- for query in benign queries:
  - run `has_sqli`
  - if true, flag as *false positive*
