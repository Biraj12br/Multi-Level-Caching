import redis

redis_client = None


def init_redis(app):

    global redis_client

    redis_client = redis.Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        decode_responses=True
    )