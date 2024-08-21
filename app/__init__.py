from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
metrics = PrometheusMetrics(app=None)
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    metrics.init_app(app)
    limiter.init_app(app)

    # Add some default metrics
    metrics.info('app_info', 'Application info', version='1.0.0')

    from app import routes, models

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    return app