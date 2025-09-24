# tests/test_services.py (relevant parts)
import pytest
from unittest.mock import Mock, patch
from services.auth_service import AuthService
from services.image_service import ImageService
from services.image_processor import ImageProcessor
from models import User, ImageUpload, ImageStatus

def test_auth_service_register_user(app):
    """Test AuthService register_user method."""
    with app.app_context():
        # Get the db instance correctly from the app context
        db = app.extensions['sqlalchemy']
        
        auth_service = AuthService(db.session)
        user, token = auth_service.register_user('testuser', 'testpassword')
        
        assert user is not None
        assert token is not None
        assert user.name == 'testuser'

def test_auth_service_register_duplicate_user(app):
    """Test AuthService register_user with duplicate user."""
    with app.app_context():
        db = app.extensions['sqlalchemy']
        
        auth_service = AuthService(db.session)
        # Register first user
        auth_service.register_user('testuser', 'testpassword')
        # Try to register same user
        user, error = auth_service.register_user('testuser', 'testpassword')
        
        assert user is None
        assert error == "User already exists"

def test_auth_service_authenticate_user(app):
    """Test AuthService authenticate_user method."""
    with app.app_context():
        db = app.extensions['sqlalchemy']
        
        auth_service = AuthService(db.session)
        # Register user first (within the same app context)
        auth_service.register_user('testuser', 'testpassword')
        # Authenticate user
        user, token = auth_service.authenticate_user('testuser', 'testpassword')
        
        assert user is not None
        assert token is not None
        # Optionally check user details
        assert user.name == 'testuser'

def test_auth_service_authenticate_invalid_user(app):
    """Test AuthService authenticate_user with invalid credentials."""
    with app.app_context():
        db = app.extensions['sqlalchemy']
        
        auth_service = AuthService(db.session)
        user, token = auth_service.authenticate_user('nonexistent', 'wrongpassword')
        
        assert user is None
        assert token is None

# ... other service tests (image_processor, file_utils) remain ...

def test_image_processor_transform_image():
    """Test ImageProcessor _transform_image method."""
    from PIL import Image
    
    processor = ImageProcessor('/tmp')
    
    # Create a test image
    test_img = Image.new('RGB', (200, 200), color='red')
    
    # Transform the image
    processed_img = processor._transform_image(test_img)
    
    assert processed_img.mode == 'L'  # Grayscale
    assert processed_img.size == (800, 600)  # Resized

def test_file_utils_allowed_file():
    """Test FileUtils allowed_file method."""
    from utils.file_utils import FileUtils
    
    assert FileUtils.allowed_file('test.jpg', {'jpg', 'png'}) == True
    assert FileUtils.allowed_file('test.txt', {'jpg', 'png'}) == False
    assert FileUtils.allowed_file('test', {'jpg', 'png'}) == False