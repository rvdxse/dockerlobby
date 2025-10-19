import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    HOST = '0.0.0.0'
    PORT = 8080