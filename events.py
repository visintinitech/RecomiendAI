import redis
import logging
from app.cache import cache

logger = logging.getLogger(__name__)

class EventPublisher:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)

    def publish_rating_update(self, user_id):
        self.redis.publish('ratings', f'user:{user_id}')
        logger.info('Evento publicado: actualización de ratings para user %s', user_id)

def start_cache_invalidator(redis_url):
    r = redis.from_url(redis_url)
    pubsub = r.pubsub()
    pubsub.subscribe('ratings')
    logger.info('Suscriptor Redis iniciado, escuchando canal ratings')

    for message in pubsub.listen():
        if message['type'] == 'message':
            user_id = message['data'].decode('utf-8').split(':')[1]
            pattern = f"get_recommendations:({user_id},*"
            cache.delete_pattern(pattern)
            logger.info('Caché invalidada para user %s', user_id)
