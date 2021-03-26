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
