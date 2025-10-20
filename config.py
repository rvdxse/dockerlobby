import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    HOST = '0.0.0.0'
    PORT = 8080
    BASIC_AUTH_USERNAME = os.environ.get('BASIC_AUTH_USERNAME') or 'admin'
    BASIC_AUTH_PASSWORD = os.environ.get('BASIC_AUTH_PASSWORD') or 'secret'

class TestingConfig(Config):
    TESTING = True
    BASIC_AUTH_USERNAME = 'test_user'
    BASIC_AUTH_PASSWORD = 'test_password'
