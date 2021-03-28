def _do_build_string(s):
    isHole = False 
    res = []
    holes = []
    lb_loc = 0 
    i = 0

    while i < len(s):
        if s[i] == '{':
            if i < len(s)-1 and s[i+1] == '{':
                res.append(('l', (i,i+1)))
                isHole = False 
                i+=1
            else: 
                isHole = True 
                lb_loc = i
        
        elif s[i] == '}':
            if isHole: 
                res.append(('h', (lb_loc,i)))
                holes.append((lb_loc,i))
                isHole = False
            elif i < len(s)-1 and s[i+1] == '}': 
                res.append(('r', (i,i+1)))
                i+=1
        i+=1
                

    print(holes)          
    print(res)  
    print()


def KETAN(hole):
    return a, b,c

def render_field(holes):
    result = []
    for hole in holes:
        value, conv, spec = KETAN(hole)
        s = value
        is_safe = False
        if isinstance(value, safe_string):
            is_safe = True 
            s = value.string

    if conv == 'r':
        trusted = value.__repr__().trusted if is_safe else [False]*len(repr(s).__format__(spec))
        result.append(trusted)
    elif conv == 's':
        trusted = value.__str__().trusted if is_safe else [False]*len(str(s).__format__(spec))
        result.append(trusted)
    elif conv == 'a':
        trusted = [False] + value.trusted + [False] if is_safe else [False]*(len(value.string)+2)
        result.append(trusted)
    else:
        trusted = value.trusted if is_safe else [False]*len(s.__format__(spec))
        result.append(trusted)

    return result


def construct_trusted(format_string, gl_holes, trusted_result): 
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
