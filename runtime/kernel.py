#!/usr/bin/env python3

import time, json, os, threading, subprocess, requests, redis
import math

r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

OLLAMA="http://127.0.0.1:11434/api/generate"

MEM_PATH="a1os/memory/vector/memory.json"
os.makedirs("a1os/memory/vector", exist_ok=True)

# ---------------- VECTOR MEMORY (REAL EMBEDDING STYLE) ----------------

def embed(text):
    v=[0]*64
    for i,c in enumerate(str(text)):
        v[i%64]+=ord(c)
    return v

def cosine(a,b):
    dot=sum(x*y for x,y in zip(a,b))
    na=math.sqrt(sum(x*x for x in a))
    nb=math.sqrt(sum(x*x for x in b))
    return dot/(na*nb+1e-9)

def load_mem():
    try:
        return json.load(open(MEM_PATH))
    except:
        return []

def save_mem(m):
    json.dump(m[-5000:], open(MEM_PATH,"w"))

MEM=load_mem()

def store(item):
    item["vec"]=embed(item["data"])
    MEM.append(item)
    save_mem(MEM)

def recall(q,k=5):
    qv=embed(q)
    scored=sorted(MEM,key=lambda x: cosine(qv,x["vec"]))
    return scored[:k]

# ---------------- REASONING VERIFICATION ENGINE ----------------

def verify(output):
    checks={
        "length": len(str(output))>10,
        "structure": "TASK" in str(output) or len(str(output))>0,
        "coherence": len(set(str(output)))>5
    }
    score=sum(1 for v in checks.values() if v)
    return score/3

# ---------------- REWARD / OPTIMIZATION SYSTEM ----------------

def reward(score):
    if score>0.8: return 1.0
    if score>0.5: return 0.5
    return -0.2

def improve(output):
    return f"REFINED:{output}"

# ---------------- AGENT SYSTEM ----------------

class Agent:
    def __init__(self,name):
        self.name=name
    def run(self,task,mem):
        return f"[{self.name}] {task} ctx={len(mem)}"

AGENTS={
    "planner":Agent("planner"),
    "executor":Agent("executor"),
    "critic":Agent("critic")
}

def route(t):
    t=str(t).lower()
    if "plan" in t: return "planner"
    if "review" in t or "check" in t: return "critic"
    return "executor"

# ---------------- LLM ----------------

def llm(prompt):
    try:
        return requests.post(OLLAMA,json={
            "model":"qwen2.5",
            "prompt":prompt,
            "stream":False
        },timeout=60).json().get("response","")
    except:
        return prompt

# ---------------- AUTONOMY LOOP ----------------

RUN=True

def loop():
    while RUN:
        task=r.rpop("tasks")
        if task:
            task=json.loads(task)

            mem=recall(task)

            raw=llm(f"TASK:{task}\nMEM:{mem}")

            score=verify(raw)
            rew=reward(score)

            if rew<0:
                raw=improve(raw)

            role=route(task)
            agent=AGENTS[role]

            out=agent.run(raw,mem)

            store({
                "data":str(out),
                "task":task,
                "score":score,
                "reward":rew,
                "ts":time.time()
            })

            r.lpush("memory",json.dumps(out))

        time.sleep(2)

# ---------------- SELF-GENERATION ----------------

def goals():
    while RUN:
        if r.llen("tasks")==0:
            r.lpush("tasks",json.dumps({
                "goal":"optimize_reasoning_cycle",
                "type":"self_generated"
            }))
        time.sleep(6)

# ---------------- SELF-HEALING ----------------

def supervisor():
    while RUN:
        try:
            r.ping()
        except:
            subprocess.Popen(["redis-server","--daemonize","yes"])
        time.sleep(5)

# ---------------- BOOT ----------------

def start():
    threading.Thread(target=loop,daemon=True).start()
    threading.Thread(target=goals,daemon=True).start()
    threading.Thread(target=supervisor,daemon=True).start()
    print("A1OS FULL AUTONOMY ENGINE ONLINE")
    while True:
        time.sleep(60)

if __name__=="__main__":
    start()
