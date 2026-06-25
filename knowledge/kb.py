import json, os
PATH="a1os/knowledge/kb.json"

def load():
    try: return json.load(open(PATH))
    except: return []

def save(data):
    json.dump(data, open(PATH,"w"))

def add(doc):
    db=load()
    db.append(doc)
    save(db)

def query(tag):
    db=load()
    return [d for d in db if tag in d.get("tags",[])]
