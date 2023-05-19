import math
import sys
import time
import uuid
import json
import jsonpickle

from example_protocol.presponses import UUIDResponse

jp_message = UUIDResponse()
json_message = {
    "name": jp_message.name,
    "data": {
        "title": ["Capitalism's Jester"] * 5000,
        "uuid": [uuid.uuid4().hex] * 5000
    }
}
jp_message.data.title = json_message["data"]["title"]
jp_message.data.uuid = json_message["data"]["uuid"]

n_iterations = 50
jp_times = {
    "dump": [0.0] * n_iterations,
    "load": [0.0] * n_iterations
}
json_times = {
    "dump": [0.0] * n_iterations,
    "load": [0.0] * n_iterations
}

for i in range(n_iterations):
    start = time.perf_counter()
    serialized = json.dumps(json_message)
    json_times["dump"][i] = time.perf_counter() - start
    start = time.perf_counter()
    json_message = json.loads(serialized)
    json_times["load"][i] = time.perf_counter() - start

    start = time.perf_counter()
    serialized = jsonpickle.dumps(jp_message)
    jp_times["dump"][i] = time.perf_counter() - start
    start = time.perf_counter()
    jp_message = jsonpickle.loads(serialized)
    jp_times["load"][i] = time.perf_counter() - start


def avg_std(data):
    factor = 1.0e3
    avg = sum(data) / len(data)
    std = math.sqrt(
        sum(
            pow(e - avg, 2) for e in data
        ) / (len(data) - 1.0)
    )
    return round(avg * factor, 3), round(std * factor, 3)

print(f"""
            Dump         |   Load         | Serialized Size in Bytes
    JP:   {avg_std(jp_times["dump"])} | {avg_std(jp_times["load"])} | {sys.getsizeof(jsonpickle.dumps(jp_message))}
    JSON: {avg_std(json_times["dump"])} | {avg_std(json_times["load"])} | {sys.getsizeof(json.dumps(json_message))}
    
""")
