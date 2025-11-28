"""
URL configuration for notes app.
"""
from django.urls import path, include # type: ignore
from rest_framework.routers import DefaultRouter # type: ignore
from .views import NoteViewSet, TagViewSet, ChatViewSet

app_name = 'notes'

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'chats', ChatViewSet, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
]
