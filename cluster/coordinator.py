import time, json, threading
from a1os.stream.bus import bus
from a1os.cluster.node import Node
from a1os.consensus.engine import consensus

results=[]

def collector():
    global results
    while True:
        r=bus.consume("results")
        if r:
            results.append(r)
        time.sleep(1)

def scheduler():
    i=0
    while True:
        bus.publish("tasks",{"msg":f"task-{i}"})
        i+=1
        time.sleep(2)

def run_cluster():
    for i in range(3):
        threading.Thread(target=Node(f"node-{i}").run,daemon=True).start()

    threading.Thread(target=collector,daemon=True).start()
    threading.Thread(target=scheduler,daemon=True).start()

    while True:
        if len(results)>5:
            leader=consensus(results[-5:])
            print("CONSENSUS LEADER:",leader)
        time.sleep(3)

if __name__=="__main__":
    run_cluster()
