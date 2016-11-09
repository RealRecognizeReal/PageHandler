#-*- coding: utf-8 -*-

def prepare(source):
    # erase style tag
    # \displaystyle, \scriptstyle

    remv = ["\displaystyle", "\scriptstyle"]
    for rem in remv:
        source = source.replace(rem, "")
    source = source.replace("  ", " ")
    source = source.replace("{ {", "{{")
    source = source.replace("} }", "}}")
    return source 

def handle(source):
    # erase useless parentheses

    source = prepare(source)

    length = len(source)
    chk = [0] * length
    stk = []
    pairs = []
    
    for i in xrange(0, length):
        if source[i] == '{':
            stk.append(i)
        elif source[i] == '}':
            l = stk.pop()
            r = i
            pairs.append([l,r])

    plength = len(pairs)

    for i in xrange(0, plength-1):
        if pairs[i][0]-1 == pairs[i+1][0]:
            if pairs[i][1]+1 == pairs[i+1][1]:
                chk[pairs[i][0]] = 1
                chk[pairs[i][1]] = 1

    data = ""
    for i in xrange(0, length):
        if chk[i] == 0:
            data += source[i]
    return data
