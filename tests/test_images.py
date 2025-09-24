# tests/test_images.py
import pytest
from io import BytesIO

def test_upload_image_unauthorized(client):
    """Test image upload without authentication."""
    data = {'file': (BytesIO(b'test image content'), 'test.jpg')}
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 401

def test_upload_image_success(client, auth_headers, create_test_image):
    """Test successful image upload."""
    test_image = create_test_image()
    data = {'file': (test_image, 'test.jpg')}
    
    response = client.post('/api/upload', 
                          data=data, 
                          headers=auth_headers,
                          content_type='multipart/form-data')
    
    assert response.status_code == 200 or response.status_code == 202
    data = response.get_json()
    assert 'image_id' in data
    assert 'message' in data

def test_upload_invalid_file_type(client, auth_headers):
    """Test uploading invalid file type."""
    data = {'file': (BytesIO(b'test content'), 'test.txt')}
    
    response = client.post('/api/upload',
                          data=data,
                          headers=auth_headers,
                          content_type='multipart/form-data')
    
    assert response.status_code == 400

def test_list_images_empty(client, auth_headers):
    """Test listing images when none exist."""
    response = client.get('/api/images', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_image_status(client, auth_headers, create_test_image):
    """Test getting image status."""
    # Upload an image first
    test_image = create_test_image()
    data = {'file': (test_image, 'test.jpg')}
    
    response = client.post('/api/upload',
                          data=data,
                          headers=auth_headers,
                          content_type='multipart/form-data')
    
    assert response.status_code in [200, 202]
    image_data = response.get_json()
    image_id = image_data['image_id']
    
    # Get image status
    response = client.get(f'/api/images/{image_id}', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['image_id'] == image_id
    assert 'status' in data

def test_get_nonexistent_image(client, auth_headers):
    """Test getting status of nonexistent image."""
    response = client.get('/api/images/99999', headers=auth_headers)
    
    assert response.status_code == 404