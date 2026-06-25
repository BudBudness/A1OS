import redis, json

r=redis.Redis(host="127.0.0.1",port=6379,decode_responses=True)

STREAM="a1os_stream"

def publish(event,data):
    r.xadd(STREAM,{"event":event,"data":json.dumps(data)})

def consume():
    items=r.xread({STREAM:"0"},count=10,block=1000)
    return items
