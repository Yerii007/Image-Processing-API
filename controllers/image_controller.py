# controllers/image_controller.py
from flask import request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.image_service import ImageService
from services.image_processor import ImageProcessor
from pathlib import Path
import os

class ImageController:
    def __init__(self, db, upload_folder, processed_folder, allowed_extensions):
        self.db = db
        self.image_service = ImageService(db.session, upload_folder, processed_folder)
        self.upload_folder = upload_folder
        self.processed_folder = processed_folder
        self.allowed_extensions = allowed_extensions
    
    @jwt_required()
    def upload_image(self):
        try:
            current_user_id = int(get_jwt_identity())
            
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400
            
            file = request.files['file']
            
            # Upload image
            image = self.image_service.upload_image(current_user_id, file, self.allowed_extensions)
            
            # Process image synchronously (for development)
            try:
                processor = ImageProcessor(self.processed_folder)
                # Use current_app.logger or a simple print function for logging
                result = processor.process_image(image, self.db.session, current_app.logger)
                
                if result.get('status') == 'completed':
                    return jsonify({
                        "message": "Image uploaded and processed successfully",
                        "image_id": image.id,
                        "original_filename": image.original_filename,
                        "status": "completed"
                    }), 200
                else:
                    return jsonify({
                        "message": "Image uploaded but processing failed",
                        "image_id": image.id,
                        "error": result.get('error')
                    }), 500
                    
            except Exception as e:
                return jsonify({
                    "message": "Image uploaded but processing failed",
                    "image_id": image.id,
                    "error": str(e)
                }), 500
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @jwt_required()
    def get_image_status(self, image_id):
        try:
            current_user_id = int(get_jwt_identity())
            image = self.image_service.get_image_by_id(image_id)
            
            self.image_service.validate_image_access(image, current_user_id)
            
            result_url = None
            if image.status == "completed" and image.result_path:
                result_url = f"/api/images/{image.id}/result"
            
            return jsonify({
                "image_id": image.id,
                "original": image.original_filename,
                "status": image.status,
                "uploaded_at": image.uploaded_at.isoformat(),
                "result_url": result_url
            })
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 404 if "not found" in str(e).lower() else 403
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @jwt_required()
    def get_processed_image(self, image_id):
        try:
            current_user_id = int(get_jwt_identity())
            image = self.image_service.get_image_by_id(image_id)
            
            self.image_service.validate_image_access(image, current_user_id)
            
            if image.status != "completed":
                return jsonify({"error": "Image not ready", "status": image.status}), 400
            if not image.result_path:
                return jsonify({"error": "No result path saved"}), 500
            
            result_path = Path(image.result_path)
            if not result_path.exists():
                return jsonify({"error": "Processed file was deleted or not saved"}), 500
            
            return send_from_directory(
                str(result_path.parent),
                str(result_path.name)
            )
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 404 if "not found" in str(e).lower() else 403
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @jwt_required()
    def list_images(self):
        try:
            current_user_id = int(get_jwt_identity())
            images = self.image_service.get_user_images(current_user_id)
            
            image_list = []
            for img in images:
                result_url = None
                if img.status == "completed" and img.result_path:
                    result_url = f"/api/images/{img.id}/result"
                
                image_list.append({
                    "image_id": img.id,
                    "original": img.original_filename,
                    "status": img.status,
                    "uploaded_at": img.uploaded_at.isoformat(),
                    "result_url": result_url
                })
            
            return jsonify(image_list)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500