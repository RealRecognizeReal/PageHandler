import threading
from difflib import SequenceMatcher
from heapq import heappush, heappop

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

lst = []

CORE = 16

with open("./merge00.out") as infile:
    for line in infile:
        lst.append(line)

SIZE = len(lst)

ass = [0] * CORE
rem = SIZE % CORE

for i in xrange(0, CORE):
    ass[i] = SIZE / CORE
    if rem > 0:
        ass[i] += 1
        rem -= 1
class mWorker (threading.Thread):

    def __init__(self, st, ed):

        threading.Thread.__init__(self)
        self.st = st
        self.ed = ed

    def doWork(self):

        print("cpal")
        
    def run(self):

        self.doWork()

goal = raw_input()
pq = []
mworker = [mWorker] * CORE
st = 0
ed = 0

for i in range(0, CORE):
    ed = st+ass[i]
    mworker[i] = mWorker(st, ed)
    st = ed
    mworker[i].start()
    
for i in range(0, CORE):
    if mworker[i].isAlive():
        mworker[i].join()
