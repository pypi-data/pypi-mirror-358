class RedisClient:
    def __init__(self, redis_conn):
        self.redis = redis_conn

    # String operations
    def set_string(self, key, value):
        self.redis.set(key, value)

    def get_string(self, key):
        return self.redis.get(key)

    # Hash operations
    def set_hash(self, key, mapping):
        self.redis.hset(key, mapping=mapping)

    def get_hash(self, key):
        return self.redis.hgetall(key)

    # List operations
    def push_list(self, key, *values):
        self.redis.rpush(key, *values)

    def get_list(self, key, start=0, end=-1):
        return self.redis.lrange(key, start, end)
