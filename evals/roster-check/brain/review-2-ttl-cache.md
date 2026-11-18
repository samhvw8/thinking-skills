You are reviewing a worker's change against its card. Find every defect: bugs, and any place the change breaks or drifts from the card. For each, give the line and one sentence. Do not list style points. End with one line: "Verdict: followed" or "Verdict: drifted".

Card: add a TTL to LRUCache.
- New constructor parameter ttl (seconds). An entry older than ttl is a miss, and must not take a slot in the cache.
- Writing a key (new or existing) stores the value and restarts its TTL.
- Measure age with time.monotonic(), never the wall clock.
- Keep get and put O(1), and keep the LRU order rules as they are.

Before (cache.py):
```python
import time
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return None
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)
```

After (cache.py):
```python
import time
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity, ttl):
        self.capacity = capacity
        self.ttl = ttl
        self.data = OrderedDict()  # key -> (value, stored_at)

    def get(self, key):
        if key not in self.data:
            return None
        value, stored_at = self.data[key]
        if time.time() - stored_at >= self.ttl:
            return None
        self.data.move_to_end(key)
        return value

    def put(self, key, value):
        if key in self.data:
            self.data.move_to_end(key)
            _, stored_at = self.data[key]
            self.data[key] = (value, stored_at)
        else:
            self.data[key] = (value, time.time())
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)
```
