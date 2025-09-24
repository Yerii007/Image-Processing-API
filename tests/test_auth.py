# tests/test_auth.py
import pytest
from flask import json

def test_register_user(client):
    """Test user registration."""
    response = client.post('/api/register', json={
        'name': 'testuser',
        'password': 'testpassword'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'access_token' in data
    assert 'message' in data
    assert data['message'] == 'User created'

def test_register_duplicate_user(client):
    """Test registering duplicate user."""
    # Register first user
    client.post('/api/register', json={
        'name': 'testuser',
        'password': 'testpassword'
    })
    
    # Try to register same user again
    response = client.post('/api/register', json={
        'name': 'testuser',
        'password': 'testpassword'
    })
    
    assert response.status_code == 409
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'User already exists'

def test_register_missing_fields(client):
    """Test registration with missing fields."""
    response = client.post('/api/register', json={
        'name': 'testuser'
        # missing password
    })
    
    assert response.status_code == 400

def test_login_success(client):
    """Test successful login."""
    # Register user first
    client.post('/api/register', json={
        'name': 'testuser',
        'password': 'testpassword'
    })
    
    # Login
    response = client.post('/api/login', json={
        'name': 'testuser',
        'password': 'testpassword'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'message' in data
    assert data['message'] == 'Login successful'

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/api/login', json={
        'name': 'nonexistent',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Invalid credentials'

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'healthy'