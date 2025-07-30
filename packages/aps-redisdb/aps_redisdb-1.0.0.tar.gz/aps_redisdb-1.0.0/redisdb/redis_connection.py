import yaml
import redis

class RedisConnectionManager:
    def __init__(self, config_file='config/redis_dbs.yml'):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        self.connections = {}

    def get_connection(self, name='default'):
        if name not in self.connections:
            conf = self.config.get(name)
            if not conf:
                raise ValueError(f"No configuration found for Redis DB: {name}")
            self.connections[name] = redis.Redis(
                host=conf['host'],
                port=conf['port'],
                db=conf['db']
            )
        return self.connections[name]