from flask import Flask
from flask_jwt_extended import JWTManager
from app.config import Config
from app.models import db
from app.auth import auth_bp
from app.routes import api_bp, recommender, event_publisher
from app.cache import RedisCache, cache
from app.events import start_cache_invalidator
import threading
import logging

logging.basicConfig(level=logging.INFO)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt = JWTManager(app)

    global cache
    cache = RedisCache(app.config['REDIS_URL'])

    global recommender
    from app.recommender import CollaborativeRecommender
    recommender = CollaborativeRecommender()

    global event_publisher
    from app.events import EventPublisher
    event_publisher = EventPublisher(app.config['REDIS_URL'])

    api_bp.recommender = recommender
    api_bp.event_publisher = event_publisher

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')

    def start_subscriber():
        from app.events import start_cache_invalidator
        start_cache_invalidator(app.config['REDIS_URL'])

    subscriber_thread = threading.Thread(target=start_subscriber, daemon=True)
    subscriber_thread.start()

    with app.app_context():
        db.create_all()

    return app
