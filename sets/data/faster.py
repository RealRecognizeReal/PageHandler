import threading
from difflib import SequenceMatcher
from heapq import heappush, heappop

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

lst = []

CORE = 16

with open("./merge00.out") as infile:
    for line in infile:
        line = line[:-1]
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

goal = raw_input()
pq = []
mworker = [mWorker] * CORE
st = 0

for i in range(0, CORE):
    ed = st+ass[i]
    mworker[i] = mWorker(st, ed, lst, pq, goal)
    st = ed
    mworker[i].start()
    
for i in range(0, CORE):
    if mworker[i].isAlive():
        mworker[i].join()

for i in range(0, 100):
    if len(pq) <= 10:
        print(heappop(pq))
        if len(pq) == 0:
            break
    else:
        heappop(pq)
