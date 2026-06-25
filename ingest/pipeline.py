import os, glob
from a1os.memory.vector_store import add
from a1os.knowledge.kb import add as kb_add

def ingest_text(path):
    text=open(path).read()
    chunks=[text[i:i+500] for i in range(0,len(text),500)]
    for c in chunks:
        add(c)
        kb_add({"text":c,"tags":["auto"]})

def run():
    for f in glob.glob("a1os/docs/*"):
        if f.endswith(".txt"):
            ingest_text(f)

if __name__=="__main__":
    run()
