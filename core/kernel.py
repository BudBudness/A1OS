import time, json, redis
from a1os.memory.vector.store import add, search
from a1os.agents.specialized.router import Router
from a1os.agents.specialized.agents import AGENTS
from a1os.learning.engine import score, improve

r=redis.Redis(host="127.0.0.1",port=6379,decode_responses=True)

router=Router()

def loop():
    while True:
        task=r.rpop("tasks")
        if task:
            task=json.loads(task)

            ctx=router.context(task)
            role=router.route(task)

            agent=AGENTS[role]
            out=agent.act(task,ctx)

            sc=score(out)
            out2=improve(out,sc)

            add(str(out2),{"role":role})

            r.lpush("memory",str(out2))

        time.sleep(2)

if __name__=="__main__":
    loop()
