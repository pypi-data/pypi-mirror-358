import time

# TODO: We could define an abstract base class called `Cache` and implement multiple cache strategies inheriting from it
class TTLCache:
    """
    This is a TTL (Time to live) cache that deletes its entries after a configured time period.

    Note: The current implementation only deletes the expired entries when they are accessed, but ideally
          we should be running a background thread that every `ttl_seconds` seconds.
    """
    class TTLEntryVal:
        def __init__(self, value, expiration_timestamp: float):
            self.value = value
            self.expiration_timestamp = expiration_timestamp

        def has_expired(self):
            current_time = time.time()
            return current_time > self.expiration_timestamp

    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self.entries: dict[str, TTLCache.TTLEntryVal] = {}

    def set(self, key, value):
        expiration_time = time.time() + self.ttl_seconds

        val = self.TTLEntryVal(value, expiration_time)
        self.entries[key] = val

    def get(self, key):
        # If the item is expired, remove it
        entry = self.entries.get(key)

        if entry is None:
            return entry

        if entry.has_expired():
            self.remove(key)
            return None

        return entry.value

    def remove(self, key):
        self.entries.pop(key, None)

