"""
Tests for note operations.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.notes.models import Note
from unittest.mock import patch, MagicMock

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def create_note():
    def make_note(user, **kwargs):
        defaults = {
            'title': 'Test Note',
            'content': 'Test content for the note.'
        }
        defaults.update(kwargs)
        return Note.objects.create(user=user, **defaults)
    return make_note


@pytest.mark.django_db
class TestNoteCreation:
    """Tests for creating notes."""
    
    @patch('apps.notes.services.gemini_service.GeminiSummarizer.generate_summary')
    def test_create_note_with_auto_summarize(self, mock_summarize, authenticated_client, user):
        """Test creating a note with auto-summarization."""
        mock_summarize.return_value = "This is a test summary."
        
        data = {
            'title': 'My Note',
            'content': 'This is a longer note content that should be summarized.',
            'auto_summarize': True
        }
        response = authenticated_client.post('/api/notes/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'My Note'
        assert Note.objects.filter(user=user, title='My Note').exists()
        mock_summarize.assert_called_once()
    
    def test_create_note_without_auto_summarize(self, authenticated_client, user):
        """Test creating a note without auto-summarization."""
        data = {
            'title': 'My Note',
            'content': 'Simple content.',
            'auto_summarize': False
        }
        response = authenticated_client.post('/api/notes/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['summary'] is None
    
    def test_create_note_unauthenticated(self, api_client):
        """Test creating a note without authentication fails."""
        data = {
            'title': 'My Note',
            'content': 'Test content.'
        }
        response = api_client.post('/api/notes/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestNoteRetrieval:
    """Tests for retrieving notes."""
    
    def test_list_notes(self, authenticated_client, user, create_note):
        """Test listing user's notes."""
        create_note(user, title='Note 1')
        create_note(user, title='Note 2')
        
        response = authenticated_client.get('/api/notes/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_list_notes_filtered_by_user(self, authenticated_client, user, create_note):
        """Test that users only see their own notes."""
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='pass123'
        )
        
        create_note(user, title='My Note')
        create_note(other_user, title='Other Note')
        
        response = authenticated_client.get('/api/notes/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'My Note'
    
    def test_retrieve_note(self, authenticated_client, user, create_note):
        """Test retrieving a single note."""
        note = create_note(user, title='Test Note')
        
        response = authenticated_client.get(f'/api/notes/{note.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Note'


@pytest.mark.django_db
class TestNoteUpdate:
    """Tests for updating notes."""
    
    def test_update_note(self, authenticated_client, user, create_note):
        """Test updating a note."""
        note = create_note(user, title='Old Title', summary='Old summary')
        
        data = {
            'title': 'New Title',
            'content': 'Updated content.'
        }
        response = authenticated_client.patch(f'/api/notes/{note.id}/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'New Title'
        
        # Verify summary is cleared when content changes
        note.refresh_from_db()
        assert note.summary is None


@pytest.mark.django_db
class TestNoteDelete:
    """Tests for deleting notes."""
    
    def test_delete_note(self, authenticated_client, user, create_note):
        """Test deleting a note."""
        note = create_note(user, title='To Delete')
        
        response = authenticated_client.delete(f'/api/notes/{note.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Note.objects.filter(id=note.id).exists()


@pytest.mark.django_db
class TestNoteSummarization:
    """Tests for manual note summarization."""
    
    @patch('apps.notes.services.gemini_service.GeminiSummarizer.generate_summary')
    def test_summarize_note(self, mock_summarize, authenticated_client, user, create_note):
        """Test manual note summarization."""
        mock_summarize.return_value = "AI generated summary."
        
        note = create_note(user, title='Test', content='Long content to summarize.')
        
        response = authenticated_client.post(f'/api/notes/{note.id}/summarize/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['summary'] == "AI generated summary."
        
        note.refresh_from_db()
        assert note.summary == "AI generated summary."
