# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config
from models import Base, User, ImageUpload
from utils import FileUtils
from controllers import HealthController, AuthController, ImageController
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db = SQLAlchemy(model_class=Base)
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Create directories
    FileUtils.create_directories(app.config['UPLOAD_FOLDER'], app.config['PROCESSED_FOLDER'])
    
    # Initialize controllers
    health_controller = HealthController(db)
    auth_controller = AuthController(db)
    image_controller = ImageController(
        db,
        app.config['UPLOAD_FOLDER'],
        app.config['PROCESSED_FOLDER'],
        app.config['ALLOWED_EXTENSIONS']
    )
    
    # Register routes
    app.add_url_rule("/health", view_func=health_controller.health_check, methods=["GET"])
    app.add_url_rule("/api/register", view_func=auth_controller.register, methods=["POST"])
    app.add_url_rule("/api/login", view_func=auth_controller.login, methods=["POST"])
    app.add_url_rule("/api/upload", view_func=image_controller.upload_image, methods=["POST"])
    app.add_url_rule("/api/images/<int:image_id>", view_func=image_controller.get_image_status, methods=["GET"])
    app.add_url_rule("/api/images/<int:image_id>/result", view_func=image_controller.get_processed_image, methods=["GET"])
    app.add_url_rule("/api/images", view_func=image_controller.list_images, methods=["GET"])
        
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)