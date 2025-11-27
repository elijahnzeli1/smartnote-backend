"""
Tests for user authentication.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def make_user(**kwargs):
        return User.objects.create_user(**kwargs)
    return make_user


@pytest.mark.django_db
class TestUserRegistration:
    """Tests for user registration."""
    
    def test_register_user_success(self, api_client):
        """Test successful user registration."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = api_client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['username'] == 'testuser'
        assert User.objects.filter(username='testuser').exists()
    
    def test_register_user_passwords_mismatch(self, api_client):
        """Test registration fails when passwords don't match."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'different123'
        }
        response = api_client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_user_duplicate_username(self, api_client, create_user):
        """Test registration fails with duplicate username."""
        create_user(username='testuser', email='existing@example.com', password='pass123')
        
        data = {
            'username': 'testuser',
            'email': 'new@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = api_client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """Tests for user login."""
    
    def test_login_success(self, api_client, create_user):
        """Test successful login returns tokens."""
        create_user(username='testuser', email='test@example.com', password='testpass123')
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = api_client.post('/api/auth/login/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
    
    def test_login_invalid_credentials(self, api_client):
        """Test login fails with invalid credentials."""
        data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        response = api_client.post('/api/auth/login/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
