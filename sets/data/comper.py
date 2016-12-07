from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

lst = []

with open("./merge.out") as infile:
    for line in infile:
        lst.append(line)

stri = "\\sqrt(x)"

Max = 0
MaxStr = ""
for item in lst:
    val = similar(item, stri)

    if Max < val:
        Max = val
        MaxStr = item

print(MaxStr)
print(Max)
