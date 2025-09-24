# tasks/image_tasks.py
from celery import Celery
from flask import current_app
from models import ImageUpload
from services import ImageProcessor, CleanupService

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

def register_tasks(celery, app, db):
    @celery.task(name="tasks.process_image")
    def process_image_task(image_id):
        with app.app_context():
            image = db.session.get(ImageUpload, image_id)
            if not image:
                current_app.logger.error(f"Image {image_id} not found")
                return {"error": "Image not found"}

            processor = ImageProcessor(app.config['PROCESSED_FOLDER'])
            return processor.process_image(image, db.session, current_app.logger)

    @celery.task(name="tasks.cleanup_old_files")
    def cleanup_old_files_task():
        with app.app_context():
            cleanup_service = CleanupService()
            return cleanup_service.cleanup_old_files(db.session, current_app.logger)
    
    return process_image_task, cleanup_old_files_task