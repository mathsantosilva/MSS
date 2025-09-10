class RedisService:
    def __init__(self, redis_client, logger):
        self.r = redis_client
        self.log = logger

    def buscar_redis_dict(self, redis_qa):
        grupos = []
        for red in redis_qa:
            if red != '':
                grupos.append(red)
        return grupos

    def limpar_todos(self):
        return self.r.flushdb()

    def limpar_por_padrao(self, pattern: str):
        removed = 0
        for key in list(self.r.scan_iter(match=pattern)):
            removed += self.r.delete(key)
        return removed
