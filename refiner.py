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
    source = source.replace("'", "'\\''") # for node
    return source

def convertLtxToMathml(ltx):
    
    ltx = "'" + ltx + "'"
    proc = muterun_js("./nodelib/converter.js", ltx)
    if proc.exitcode == 0:
        if "<merror>" in proc.stdout:
            raise Exception
        else:
            return proc.stdout
    else:
        raise Exception

print(prepare("\\lim_{t\\to 0^+}\\frac{f(g(t))-f(x_0)}{t} = u(g'(0))."))
print(convertLtxToMathml(prepare("\\lim_{t\\to 0^+}\\frac{f(g(t))-f(x_0)}{t} = u(g'(0)).")))
