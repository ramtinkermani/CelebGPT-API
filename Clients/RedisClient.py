import redis
import json

from starlette.responses import JSONResponse


class RedisClient():
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, decode_responses=True)

    async def getItem(self, key):
        normalized_key = key.lower().replace(" ", "_")
        value = self.client.get(normalized_key)
        if value:
            return {"key": normalized_key, "value": value}
        else:
            return None

    async def setItem(self, key, value, ex=0):
        normalized_key = key.lower().replace(" ", "_")
        if type(value) in [list, dict]:
            value = json.dumps(value)

        if ex == 0:
            # No expiration
            self.client.set(normalized_key, value)
        else:
            self.client.set(normalized_key, value)
        return {"message": f"key/value set for key {normalized_key}"}

class RedisEndpoints:
    @staticmethod
    async def redis_get(request):
        payload = await request.json()
        key = payload['key']

        redis_client = RedisClient()
        result = await redis_client.getItem(key)
        return JSONResponse(result, 200)

    @staticmethod
    async def redis_set(self, request):
        payload = await request.json()
        key = payload['key']
        value = payload['value']

        redis_client = RedisClient()
        result = await redis_client.setItem(key, value)
        return JSONResponse(result, 200)