# str.format


"fmt string {field!conv:spec}".format(1, 2, 3, key="blah", num=5, obj=Person())


"   {{ }}  {f1}          {f2}       {f3}        ".format(....)
[          ----          ----       ----        ]

f1 : arg1
f2 : arg3
f3 : arg9


```python
def render_field():
  if conv1 == 'r':
    return repr(arg1).__format__(spec1)
  elif conv1 == 's':
    return str(arg1).__format__(spec1)
  elif conv1 == 'a':
    return ascii(arg1).__format__(spec1)
  else:
    return arg1.__format__(spec1)
```

## Pseudocode
1. find start, end of each field hole # use single-pass, counting { and }'s # `_do_build_string`
2. relate each field hole to an argument # `_get_argument` (make sure to do lookup)
3. call `render_field()` on it to get length # `self._render_field`
4. if argument is a `safe_string`, use its trusted array, otherwise use [False...]
5. replace trusted arrays in the field holes
6. call `str.format` to get final string

## References
objspace/std/newformat.py

## TODO: make sure ascii() works correctly on safestring
