from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
from config import Config

db = SQLAlchemy()
metrics = PrometheusMetrics(app=None)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    metrics.init_app(app)

    # Add some default metrics
    metrics.info('app_info', 'Application info', version='1.0.0')

    from app import routes, models

    return app