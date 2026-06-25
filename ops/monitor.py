import time
from a1os.broker.streams import r, STREAM

while True:
    print({
        "stream_len": len(r.xrange(STREAM)),
        "redis": r.ping()
    })
    time.sleep(5)
