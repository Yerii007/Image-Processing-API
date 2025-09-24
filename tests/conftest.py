# tests/conftest.py
import pytest
import os
import tempfile

# --- Fixtures for the Flask application ---
@pytest.fixture
def app():
    """Create application for testing."""

    # --- Create temporary resources FIRST ---
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    # Create temporary directories for uploads
    upload_folder = tempfile.mkdtemp()
    processed_folder = tempfile.mkdtemp()

    # --- Define the test configuration class ---
    # Define it inside the fixture so it can use the variables from above
    class TestConfig:
        TESTING = True
        SECRET_KEY = 'test-secret-key-for-testing'
        JWT_SECRET_KEY = 'test-jwt-secret-key-for-testing'

        # --- Use the pre-created temporary paths ---
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        SQLALCHEMY_TRACK_MODIFICATIONS = False

        UPLOAD_FOLDER = upload_folder
        PROCESSED_FOLDER = processed_folder
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

        # Celery settings for testing (if needed by app startup)
        CELERY_BROKER_URL = 'memory://'
        CELERY_RESULT_BACKEND = 'cache+memory://'

    # --- Import your application factory ---
    from app import create_app

    # --- Create the app instance using the test config class ---
    app = create_app(TestConfig)

    # --- Store test-specific resources in app config for cleanup ---
    # Attach the file descriptor and paths to the app config
    app.config['TEST_DB_FD'] = db_fd
    app.config['TEST_DB_PATH'] = db_path
    app.config['TEST_UPLOAD_FOLDER'] = upload_folder
    app.config['TEST_PROCESSED_FOLDER'] = processed_folder

    # --- Ensure the app context is available and tables are created ---
    with app.app_context():
        # Import the db instance correctly based on your app structure
        # Since your app.py creates `db` locally, you need to access the one
        # attached to the app instance.
        # The `db` created in `app.py` is registered with the app.
        db = app.extensions['sqlalchemy'] # Get the db instance registered with the app
        db.create_all() # Create tables within the test app's context

        yield app # Provide the app instance to the test

        # --- Cleanup after tests ---
        # Close and remove the temporary database file
        try:
            # Get the stored file descriptor and path
            test_db_fd = app.config.get('TEST_DB_FD')
            test_db_path = app.config.get('TEST_DB_PATH')

            if test_db_fd is not None:
                os.close(test_db_fd)
            if test_db_path and os.path.exists(test_db_path):
                os.unlink(test_db_path)
        except (OSError, KeyError, TypeError):
            pass # Ignore cleanup errors

        # Cleanup temporary directories
        import shutil
        try:
            upload_dir = app.config.get('TEST_UPLOAD_FOLDER')
            processed_dir = app.config.get('TEST_PROCESSED_FOLDER')

            if upload_dir and os.path.exists(upload_dir):
                shutil.rmtree(upload_dir, ignore_errors=True)
            if processed_dir and os.path.exists(processed_dir):
                shutil.rmtree(processed_dir, ignore_errors=True)
        except (OSError, KeyError, TypeError):
            pass # Ignore cleanup errors

# --- Standard pytest-flask fixtures ---
@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()

# --- Fixtures for authenticated requests ---
@pytest.fixture
def auth_headers(client):
    """Registers a test user and returns authentication headers."""
    # Register a test user
    response = client.post('/api/register', json={
        'name': 'testuser',
        'password': 'testpassword123'
    })

    if response.status_code == 201:
        token = response.get_json()['access_token']
        return {'Authorization': f'Bearer {token}'}
    else:
        # If registration fails, provide empty headers or handle error
        # pytest.fail(f"Failed to create test user: {response.get_json()}")
        # Returning empty dict is often simpler for tests expecting failure
        # Or you could make this fixture yield None/raise if user creation is critical
        return {}

@pytest.fixture
def create_user(app):
    """Factory fixture to create test users."""
    def _create_user(name='testuser', password='testpassword123'):
        with app.app_context():
            from services.auth_service import AuthService
            # Get the db instance correctly from the app context
            db = app.extensions['sqlalchemy']

            auth_service = AuthService(db.session)
            user, token = auth_service.register_user(name, password)
            return user, token
    return _create_user

@pytest.fixture
def create_test_image():
    """Fixture to create a simple test image file-like object."""
    def _create_test_image(format='JPEG'):
        from PIL import Image
        import io

        # Create a simple red square image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0) # Reset pointer to beginning
        return img_bytes
    return _create_test_image

# Optional: If you need direct access to the test database session
# This is often handled by the app fixture and client, but can be useful
# @pytest.fixture
# def db_session(app):
#     with app.app_context():
#         db = app.extensions['sqlalchemy']
#         yield db.session
#         # Rollback any changes made during the test if needed
#         # db.session.rollback() # Uncomment if you want automatic rollback