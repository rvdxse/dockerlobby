from flask import Flask
from config import Config
from .routes import bp as main_bp
from .services import DockerManager
import os
import docker

def create_app(config_class=Config):
    template_dir = os.path.abspath('./templates')
    static_dir = os.path.abspath('./static')
    
    app = Flask('app', template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)

    try:
        docker_client = docker.from_env(timeout=30)
        app.container_manager = DockerManager(docker_client)
    except Exception as e:
        print(f"FATAL: Could not connect to Docker daemon: {e}")
        app.container_manager = None
        
    app.register_blueprint(main_bp)

    return app
