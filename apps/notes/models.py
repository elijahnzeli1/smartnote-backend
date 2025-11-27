"""
Note models for the Smart Notes application.
"""
from django.db import models # type: ignore
from django.conf import settings # type: ignore


class Tag(models.Model):
    """
    Model representing a tag for organizing notes.
    """
    name = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tags'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tags'
        ordering = ['name']
        unique_together = ['name', 'user']
        indexes = [
            models.Index(fields=['user', 'name']),
        ]
    
    def __str__(self):
        return self.name


class Note(models.Model):
    """
    Model representing a user's note with optional AI-generated summary.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='notes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
