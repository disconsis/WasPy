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


## Fronts
- Tests
  - imp [marked yellow] -> do first

- Automatic str replacements
  - then: Benchmark on a large open-source project

### Automatic str replacements
1. source code replacement

change all `"abc"` in code to `safe_string("abc", trusted=True)`

```python

safe_string("ketan ") + safe_string("blah")
safe_string("my name is ") + input()
```

Problems:

How to handle new str -> `safe_string` replacements
```python
input() + safe_string(" is my name")
input().format(safe_string("blah"))
```

possible solution: override some list of functions

2. change CPython interpreter

- allocate `safe_string` instead of str
- make sure actual str's are allocated inside `safe_string` module
- prevent recursion


3. change python magic functions (don't know which) which allocate str objects



Problem:
- need to make sure output functions get actual string
```python
print(input())
print("name")
db_request()
http_request()
```

- make special case for sql query method
  - call has_sqli function



```

source.py -----python compiler----> python bytecode
                                          |
                                          |
                                waspy preprocess bytecode
                                          |
                                          |
                                    python bytecode vm
                                          |
                                          |
                                          |
                                          V
                                    execute program

```



























# TODO

## Override `cursor.execute`
1. Find most popular low-level libraries (connector libraries?) for top DBs:
- [X] sqlite3
- [ ] mysql
- [ ] postgres - psycopg2

2. Wrap them with `has_sqli`

* Only run `has_sqli` on first argument.

## Run against sample applications
- Search for non-sqli payloads
- False positives/negatives

```python

for payload in sqli_payloads:
   if has_sqli(payload) == False and is_valid(payload):
      raise FalseNegative
      
for payload in non_sqli_payloads:
   if has_sqli(payload) == True and is_valid(payload):
      raise FalsePositive

```

Build some sample applications and test some inputs against them.
- https://github.com/captain-yuca/hurricane-relief-be
  - postgres
- https://github.com/yi-jiayu/sqli-example
  - sqlite3
- https://github.com/stamparm/DSVW
  - sqlite3

## Fix breakages in `compile` and other functions like it
Builtin C functions which call `PyUnicode_CheckExact` to ensure they get a
unicode object (and not a subtype) throw this error. This is a list
of them:
1. compile

Override these to convert their arguments to unsafe string beforehand.

## Validate
1. first check if `has_sqli`
2. sqlvalidator

If lot of false positives/negatives:
3. use EXPLAIN (**which db?**)
  - go through all of them to find any one which thinks this is valid
