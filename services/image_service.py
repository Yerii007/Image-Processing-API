from sqlalchemy import select
from models.image import ImageUpload, ImageStatus
from models.users import User
from utils.file_utils import FileUtils
import os

class ImageService:
    def __init__(self, db_session, upload_folder, processed_folder):
        self.db_session = db_session
        self.upload_folder = upload_folder
        self.processed_folder = processed_folder
    
    def upload_image(self, user_id, file, allowed_extensions):
        # Validate file
        if not file or file.filename == '':
            raise ValueError("No file provided")
        
        if not FileUtils.allowed_file(file.filename, allowed_extensions):
            raise ValueError("Invalid file type")
        
        # Save file
        filename = f"{user_id}_{file.filename}"
        upload_path = os.path.join(self.upload_folder, filename)
        file.save(upload_path)
        
        # Create image record
        image = ImageUpload(
            user_id=user_id,
            original_filename=file.filename,
            upload_path=upload_path,
            status=ImageStatus.PENDING.value
        )
        self.db_session.add(image)
        self.db_session.commit()
        
        return image
    
    def get_user_images(self, user_id):
        return self.db_session.execute(
            select(ImageUpload).where(ImageUpload.user_id == user_id)
        ).scalars().all()
    
    def get_image_by_id(self, image_id):
        return self.db_session.get(ImageUpload, image_id)
    
    def validate_image_access(self, image, user_id):
        if not image:
            raise ValueError("Image not found")
        if image.user_id != user_id:
            raise ValueError("Access denied")