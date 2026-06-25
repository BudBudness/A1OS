from a1os.broker.streams import r, STREAM

def sync_state():
    data=r.xrange(STREAM)
    return len(data)
