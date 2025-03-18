from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS with specific origins
    CORS(app, resources={
        r"/*": {
            "origins": [
                "https://playdber.me",
                "http://playdber.me",
                "https://www.playdber.me",
                "http://www.playdber.me"
            ]
        }
    })
    
    db.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app 