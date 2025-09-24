# services/image_processor.py
import os
from PIL import Image, UnidentifiedImageError
from models.image import ImageStatus
from utils.file_utils import FileUtils

class ImageProcessor:
    def __init__(self, processed_folder):
        self.processed_folder = processed_folder
    
    def process_image(self, image, db_session, app_logger):
        try:
            image.status = ImageStatus.PROCESSING.value
            db_session.commit()
            app_logger.info(f"Processing image {image.id}")

            input_path = image.upload_path
            output_filename = f"processed_{os.path.basename(image.upload_path)}"
            output_path = os.path.join(self.processed_folder, output_filename)

            # Validate image
            try:
                img = Image.open(input_path)
                img.verify()
                img = Image.open(input_path) 
            except UnidentifiedImageError:
                image.status = ImageStatus.FAILED.value
                db_session.commit()
                app_logger.error(f"Invalid image file: {input_path}")
                return {"status": "failed", "error": "Invalid image file"}

            # Process image
            processed_img = self._transform_image(img)
            processed_img.save(output_path, "JPEG")

            image.result_path = output_path
            image.status = ImageStatus.COMPLETED.value
            db_session.commit()

            app_logger.info(f"Image {image.id} processed successfully")
            return {"status": "completed", "result": output_path}

        except Exception as e:
            image.status = ImageStatus.FAILED.value
            db_session.commit()
            app_logger.error(f"Failed to process image {image.id}: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _transform_image(self, img):
        """Apply image transformations"""
        img = img.convert("L")  # Convert to grayscale
        img = img.resize((800, 600))  # Resize to 800x600
        return img