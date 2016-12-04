#-*- coding: utf-8 -*-
from Naked.toolshed.shell import muterun_js

def prepare(source):
    # erase style tag

    remv = ["\\displaystyle", "\\scriptstyle", "\\textstyle"]
    for rem in remv:
        source = source.replace(rem, "")
    source = source.replace("\\dfrac", "\\frac")
    source = source.replace("\\tfrac", "\\frac")
    source = source.replace("\\tbinom", "\\binom")
    source = source.replace("\\dbinom", "\\binom")
    source = source.replace("\\mybinom", "\\binom")
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
            try:
                l = stk.pop()
                r = i
                pairs.append([l,r])
            except:
                raise Exception

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

def convertLtxToMathml(ltx):
    
    proc = muterun_js("./nodelib/converter.js", ltx)
    if proc.exitcode == 0:
        if "<merror>" in proc.stdout:
            raise Exception
        else:
            return proc.stdout
    else:
        raise Exception
