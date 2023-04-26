import redis

r = redis.Redis(host='192.168.50.100', port=6379, decode_responses=True)

r.hset('sensor_door:1', mapping = {"open":'true'})
r.hset('sensor_door:2', mapping = {"open":'true'})
r.hset('sensor_door:3', mapping = {"open":'false'})

r.hset('sensor_window:1', mapping = {"open":'false'})

print(r.hgetall("sensor_door:1"))

# bar