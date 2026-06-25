import sqlite3, json, math

DB="a1os/vector/vdb.sqlite"

def conn():
    return sqlite3.connect(DB)

def init():
    c=conn()
    c.execute("CREATE TABLE IF NOT EXISTS vectors(id INTEGER PRIMARY KEY, node TEXT, text TEXT, vec TEXT)")
    c.commit(); c.close()

def embed(t):
    v=[0]*256
    for i,c in enumerate(str(t)):
        v[i%256]+=ord(c)
    return v

def cos(a,b):
    dot=sum(x*y for x,y in zip(a,b))
    na=math.sqrt(sum(x*x for x in a))
    nb=math.sqrt(sum(x*x for x in b))
    return dot/(na*nb+1e-9)

def put(node,text):
    init()
    v=embed(text)
    c=conn()
    c.execute("INSERT INTO vectors(node,text,vec) VALUES(?,?,?)",
              (node,text,json.dumps(v)))
    c.commit(); c.close()

def query(q,k=5):
    init()
    qv=embed(q)
    c=conn()
    rows=c.execute("SELECT text,vec FROM vectors").fetchall()
    scored=[]
    for t,v in rows:
        scored.append((cos(qv,json.loads(v)),t))
    return [t for _,t in sorted(scored,reverse=True)[:k]]
