from flask import Flask
from .api_services import bp as services_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(services_bp)
    return app
