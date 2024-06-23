import time


class timelyProperty:
    def __init__(self, func, ttl=10):
        self.func = func
        self.ttl = ttl
        self.cache = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self

        current_time = time.time()
        cache_entry = self.cache.get(instance)

        if cache_entry and (current_time < cache_entry["expire_time"]):
            return cache_entry["value"]

        # Cache is expired or not set, recalculate and update
        value = self.func(instance)
        self.cache[instance] = {"value": value, "expire_time": current_time + self.ttl}
        return value

    def __delete__(self, instance):
        if instance in self.cache:
            del self.cache[instance]


class timelyClsProperty:
    def __init__(self, func, ttl=10):  # Default TTL is set to 10 seconds
        self.func = func
        self.ttl = ttl
        self.cache = {}

    def __get__(self, instance, owner):
        current_time = time.time()
        cache_entry = self.cache.get(owner)

        if cache_entry and (current_time < cache_entry["expire_time"]):
            return cache_entry["value"]

        # Cache is expired or not set, recalculate and update
        value = self.func(owner)
        self.cache[owner] = {"value": value, "expire_time": current_time + self.ttl}
        return value

    def __delete__(self, owner):
        if owner in self.cache:
            del self.cache[owner]
