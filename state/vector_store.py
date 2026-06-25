import json, sqlite3

DB="a1os/state/vectors.db"

def conn():
    return sqlite3.connect(DB)

def init():
    c=conn()
    c.execute("CREATE TABLE IF NOT EXISTS vectors(id INTEGER PRIMARY KEY, text TEXT, meta TEXT)")
    c.commit(); c.close()

def add(text,meta={}):
    init()
    c=conn()
    c.execute("INSERT INTO vectors(text,meta) VALUES(?,?)",(text,json.dumps(meta)))
    c.commit(); c.close()

def all():
    c=conn()
    r=c.execute("SELECT text,meta FROM vectors").fetchall()
    c.close()
    return r
