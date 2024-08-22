from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_migrate import Migrate
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
metrics = PrometheusMetrics(app=None)
limiter = Limiter(key_func=get_remote_address)
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    metrics.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import and register blueprint
        from app.routes import main as main_blueprint
        app.register_blueprint(main_blueprint)

        # Import models
        from app import models

        # Register the metric
        try:
            metrics.info('app_info', 'Application info', version='1.0.0')
        except Exception as e:
            app.logger.warning(f"Failed to register app_info metric: {str(e)}")

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    return app