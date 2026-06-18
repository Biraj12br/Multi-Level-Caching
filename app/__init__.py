from flask import Flask

from app.extensions import db

from app.config.config import Config

from app.api.rules import rules_bp

from app.cache.redis_cache import init_redis

from app.handlers.error_handler import (
    register_error_handlers
)

from app.handlers.logger import (
    configure_logger
)


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    configure_logger()

    db.init_app(app)

    init_redis(app)

    app.register_blueprint(rules_bp)

    register_error_handlers(app)

    return app