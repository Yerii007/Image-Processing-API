from datetime import datetime, timedelta
from models.image import ImageUpload
from utils.file_utils import FileUtils

class CleanupService:
    def __init__(self):
        pass
    
    def cleanup_old_files(self, db_session, app_logger, days_old=1):
        try:
            cutoff = datetime.utcnow() - timedelta(days=days_old)
            
            # Query old images
            old_images = db_session.query(ImageUpload).filter(
                ImageUpload.uploaded_at < cutoff
            ).all()

            deleted_count = 0
            for img in old_images:
                # Delete associated files
                for path in [img.upload_path, img.result_path]:
                    FileUtils.delete_file(path)
                
                # Delete database record
                db_session.delete(img)
                deleted_count += 1

            db_session.commit()
            app_logger.info(f"Cleanup complete: {deleted_count} old images removed")
            return deleted_count
            
        except Exception as e:
            app_logger.error(f"Cleanup task failed: {e}")
            db_session.rollback()
            raise