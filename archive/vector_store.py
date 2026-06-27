import sqlite3, json, math

DB="a1os/memory/vector.db"

def conn():
    return sqlite3.connect(DB)

def init():
    c=conn()
    c.execute("CREATE TABLE IF NOT EXISTS chunks(id INTEGER PRIMARY KEY, text TEXT, vec TEXT)")
    c.commit(); c.close()

def embed(text):
    v=[0]*64
    for i,c in enumerate(text):
        v[i%64]+=ord(c)
    return v

def cosine(a,b):
    dot=sum(x*y for x,y in zip(a,b))
    na=math.sqrt(sum(x*x for x in a))
    nb=math.sqrt(sum(x*x for x in b))
    return dot/(na*nb+1e-9)

def add(text):
    init()
    v=embed(text)
    c=conn()
    c.execute("INSERT INTO chunks(text,vec) VALUES(?,?)",(text,json.dumps(v)))
    c.commit(); c.close()

def search(q):
    init()
    vq=embed(q)
    c=conn()
    rows=c.execute("SELECT text,vec FROM chunks").fetchall()
    scored=[]
    for t,v in rows:
        vec=json.loads(v)
        scored.append((cosine(vq,vec),t))
    return [t for _,t in sorted(scored,reverse=True)[:5]]
