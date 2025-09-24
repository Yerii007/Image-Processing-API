import os
from pathlib import Path
from werkzeug.utils import secure_filename

class FileUtils:
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def create_directories(upload_folder, processed_folder):
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(processed_folder, exist_ok=True)
    
    @staticmethod
    def secure_save_file(file, upload_path):
        filename = secure_filename(file.filename)
        full_path = os.path.join(upload_path, filename)
        file.save(full_path)
        return full_path
    
    @staticmethod
    def delete_file(file_path):
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
        return False