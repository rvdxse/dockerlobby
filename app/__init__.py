from flask import Flask
from config import Config
from .routes import bp as main_bp
import os
def create_app():
    template_dir = os.path.abspath('./templates')
    static_dir = os.path.abspath('./static')
    app = Flask('app',template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)
    app.register_blueprint(main_bp)

    return app