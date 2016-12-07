import threading
import sys
from difflib import SequenceMatcher
from heapq import heappush, heappop

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

CORE = 16

prev = ""

ltx_mapper = {}

# key: latex, value: array of url

# key: x^2 url: ab, bc, de

# dict["x^2"] = ["ab"]
# dict["x^2"].append("bc")
with open("./merge.out") as infile:
    for line in infile:
        line = line[:-1]

        if len(line) <= 0:
            prev = line
            continue

        if line[0] == '2':
            ltx = prev
            url = line[2:]
            
            if ltx not in ltx_mapper.keys():
                ltx_mapper[ltx] = []
            
            ltx_mapper[ltx].append(url)
            
        prev = line[2:]

SIZE = len(ltx_mapper.keys())

ass = [0] * CORE
rem = SIZE % CORE

for i in xrange(0, CORE):
    ass[i] = SIZE / CORE
    if rem > 0:
        ass[i] += 1
        rem -= 1

class mWorker (threading.Thread):

    def __init__(self, st, ed, lst, pq, goal):

        threading.Thread.__init__(self)
        self.st = st
        self.ed = ed
        self.lst = lst
        self.pq = pq
        self.goal = goal

    def doWork(self):

        for i in xrange(self.st, self.ed):
            e = similar(self.goal, self.lst[i])
            heappush(self.pq, (e, self.lst[i]))
            while len(self.pq) > 100:
                heappop(self.pq)
        
    def run(self):

        self.doWork()

goal = str(sys.argv[1])
pq = []
mworker = [mWorker] * CORE
st = 0

for i in range(0, CORE):
    ed = st+ass[i]
    mworker[i] = mWorker(st, ed, ltx_mapper.keys(), pq, goal)
    st = ed
    mworker[i].start()
    
for i in range(0, CORE):
    if mworker[i].isAlive():
        mworker[i].join()

temp = []

for i in range(0, 100):
    if len(pq) <= 10:
        (e, ltx) = heappop(pq)
        temp.append(ltx_mapper[ltx])
        if len(pq) == 0:
            break
    else:
        heappop(pq)

temp.reverse()

answer = []

for urls in temp:
    for url in urls:
        if url in answer:
            continue
        else:
            answer.append(url)
            if len(answer) == 10:
                break
    if len(answer) == 10:
        break

for output in answer:
    print(output)
