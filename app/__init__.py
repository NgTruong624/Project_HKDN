from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Cấu hình CORS - cho phép tất cả nguồn truy cập
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    # Thêm middleware để xử lý CORS thủ công nếu cần
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,X-CSRF-Token')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    # Cấu hình database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///players.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    
    # Import và đăng ký blueprint
    from app.routes import main
    app.register_blueprint(main)
    
    # Tạo database nếu chưa tồn tại
    with app.app_context():
        db.create_all()
    
    return app 