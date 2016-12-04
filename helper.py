import latex2mathml.converter
from Naked.toolshed.shell import execute_js, muterun_js

e = "sexy"
e = e.replace("?exy", "exy")
print(e)

print(latex2mathml.converter.convert("\\frac {n}{m}"))
print(latex2mathml.converter.convert("3!"))

proc = muterun_js("./nodelib/converter.js", "3!")

if proc.exitcode == 0:
    print(proc.stdout)
else:
    print("Error")
