# celery_app.py
from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import Base, ImageUpload
from services import ImageProcessor, CleanupService

def create_celery_app():
    # Create Flask app for Celery worker context
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db = SQLAlchemy(model_class=Base)
    db.init_app(app)
    
    # Create Celery instance with proper configuration
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    
    # Update Celery configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    
    # Define tasks properly
    @celery.task(name="tasks.process_image")
    def process_image_task(image_id):
        with app.app_context():
            try:
                # Re-initialize database session for Celery worker
                image = db.session.get(ImageUpload, image_id)
                if not image:
                    app.logger.error(f"Image {image_id} not found")
                    return {"error": "Image not found"}

                app.logger.info(f"Processing image {image_id}")
                
                processor = ImageProcessor(app.config['PROCESSED_FOLDER'])
                result = processor.process_image(image, db.session, app.logger)
                
                app.logger.info(f"Image processing completed: {result}")
                return result
                
            except Exception as e:
                app.logger.error(f"Error processing image {image_id}: {str(e)}")
                return {"error": str(e)}

    @celery.task(name="tasks.cleanup_old_files")
    def cleanup_old_files_task():
        with app.app_context():
            try:
                app.logger.info("Starting cleanup task")
                cleanup_service = CleanupService()
                result = cleanup_service.cleanup_old_files(db.session, app.logger)
                app.logger.info(f"Cleanup completed: {result} files removed")
                return {"status": "completed", "files_removed": result}
                
            except Exception as e:
                app.logger.error(f"Error in cleanup task: {str(e)}")
                return {"error": str(e)}
    
    return celery

# Create the Celery app instance
celery = create_celery_app()

if __name__ == '__main__':
    celery.start()