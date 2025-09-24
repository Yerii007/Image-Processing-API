# tests/test_models.py
import pytest
from models import User, ImageUpload, ImageStatus
from werkzeug.security import check_password_hash

def test_user_model(app): # 'app' fixture is injected
    """Test User model."""
    with app.app_context(): # Use the app context provided by the fixture
        # Get the db instance from the app context
        # The key 'sqlalchemy' is the default used by Flask-SQLAlchemy
        db = app.extensions['sqlalchemy'] 
        
        user = User(name='testuser')
        user.set_password('testpassword')
        
        assert user.name == 'testuser'
        assert check_password_hash(user.password, 'testpassword')
        assert user.check_password('testpassword') == True
        assert user.check_password('wrongpassword') == False

def test_image_upload_model(app):
    """Test ImageUpload model."""
    with app.app_context():
        db = app.extensions['sqlalchemy'] # Get db from app context
        
        image = ImageUpload(
            user_id=1,
            original_filename='test.jpg',
            upload_path='/path/to/test.jpg',
            status=ImageStatus.PENDING.value
        )
        
        assert image.user_id == 1
        assert image.original_filename == 'test.jpg'
        assert image.upload_path == '/path/to/test.jpg'
        assert image.status == ImageStatus.PENDING.value
        assert image.task_id is None
        assert image.result_path is None

def test_user_to_dict(app):
    """Test User model to_dict method."""
    with app.app_context():
        # db not strictly needed for this simple test, but shown for consistency
        # db = app.extensions['sqlalchemy']
        
        user = User(name='testuser')
        user.id = 1 # Simulate an ID after saving
        
        user_dict = user.to_dict()
        assert user_dict['id'] == 1
        assert user_dict['name'] == 'testuser'

def test_image_to_dict(app):
    """Test ImageUpload model to_dict method."""
    with app.app_context():
        from datetime import datetime # Import datetime
        db = app.extensions['sqlalchemy']
        
        # Create an image instance with required fields
        image = ImageUpload(
            user_id=1,
            original_filename='test.jpg',
            upload_path='/path/to/test.jpg'
            # status defaults to PENDING
            # uploaded_at defaults to datetime.utcnow via the model definition
        )
        
        # Simulate saving to DB to get an ID and ensure uploaded_at is set
        # This is important for to_dict to work correctly
        db.session.add(image)
        db.session.commit() # This will assign ID and set uploaded_at
        
        # Now call to_dict
        image_dict = image.to_dict()
        assert 'id' in image_dict # Should now have an ID
        assert 'user_id' in image_dict
        assert 'original_filename' in image_dict
        assert 'status' in image_dict
        assert 'uploaded_at' in image_dict
        # Check that uploaded_at is a string (isoformat)
        assert isinstance(image_dict['uploaded_at'], str)
        # Check the format roughly (basic check)
        assert 'T' in image_dict['uploaded_at']
