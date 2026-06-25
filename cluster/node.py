import os, time, json
from multiprocessing import Process
from a1os.broker.streams import publish

def worker(node_id):
    i=0
    while True:
        publish("task",{"node":node_id,"task":f"work-{i}"})
        i+=1
        time.sleep(2)

def start_nodes(n=3):
    procs=[]
    for i in range(n):
        p=Process(target=worker,args=(f"node-{i}",))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
