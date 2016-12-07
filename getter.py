import pymongo
import sys
import threading
import multiprocessing
import refiner

CORE = 16
class Counter(object):
    def __init__(self):
        self.cnt = multiprocessing.Value('i', 0)

    def increment(self, n=1):
        with self.cnt.get_lock():
            self.cnt.value += n

    @property
    def value(self):
        return self.cnt.value

class myJWorker (threading.Thread):

    def __init__(self, i, fsets, lock, currentIdx, totalSize):
        threading.Thread.__init__(self)
        self.i = i
        self.fsets = fsets
        self.currentIdx = currentIdx
        self.totalSize = totalSize
        self.lock = lock

        try:
            self.con = pymongo.MongoClient("slb-283692.ncloudslb.com", 27017)
        except:
            print("fucking db")
            raise Exception

        self.db = self.con.alan
        self.dbp = self.db.page

    def doWork(self):

        BUCKET_PAGE_SIZE = 10
        LIMIT_FORMULA_SIZE = 100000

        fp = open("./sets/"+str(i)+".out", "w")

        while self.totalSize.cnt.value < LIMIT_FORMULA_SIZE:
            
            idx = 0
            with self.lock:
                idx = self.currentIdx.cnt.value
                self.currentIdx.increment()
            
            start = idx*BUCKET_PAGE_SIZE
            data = self.dbp.find({"formulasNumber": {"$gt": 0}}).skip(start).limit(BUCKET_PAGE_SIZE)

            if data is None:
                break

            for datum in data:
                formulas = datum["formulas"]
                formulasNumber = datum["formulasNumber"]
                url = datum["url"]
                
                cnt = 0
                for formula in formulas:
                    latex = formula["latex"]
                    latex = refiner.prepare(latex)

                    keys = (latex, url)

                    if keys in self.fsets:
                        continue #exists

                    self.fsets[keys] = 1

                    try:
                        fp.write("1 " + latex+"\n2 "+url+"\n")
                        cnt += 1
                    except:
                        continue #error
                
                with self.lock:
                    self.totalSize.increment(cnt)

            print(str(idx)+ " is finished")
        self.con.close()
        fp.close()

    def run(self):
        self.doWork()

currentIdx = Counter()
totalSize = Counter()
lock = multiprocessing.Lock()
fsets = {}

jworker = [myJWorker] * CORE
for i in range(0, CORE):
    jworker[i] = myJWorker(i, fsets, lock, currentIdx, totalSize)
    jworker[i].start()

for i in range(0, CORE):
    if jworker[i].isAlive():
        jworker[i].join()
