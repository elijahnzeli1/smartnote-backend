"""
Note models for the Smart Notes application.
"""
from django.db import models # type: ignore
from django.conf import settings # type: ignore
from django.utils import timezone # type: ignore


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


class Chat(models.Model):
    """
    Model representing a chat conversation with AI context.
    Stores both the full chat history and AI-generated summaries.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chats'
    )
    title = models.CharField(max_length=200, blank=True)
    summary = models.TextField(
        blank=True,
        null=True,
        help_text="AI-generated summary of the entire conversation"
    )
    context_summary = models.TextField(
        blank=True,
        null=True,
        help_text="Condensed context for AI to understand the conversation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    message_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'chats'
        ordering = ['-last_message_at', '-created_at']
        indexes = [
            models.Index(fields=['user', '-last_message_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title or f'Chat {self.id}'} - {self.user.username}"
    
    def update_summary(self, new_summary: str):
        """Update the chat summary and timestamp."""
        self.summary = new_summary
        self.updated_at = timezone.now()
        self.save(update_fields=['summary', 'updated_at'])
    
    def update_context(self, context: str):
        """Update the context summary for AI."""
        self.context_summary = context
        self.updated_at = timezone.now()
        self.save(update_fields=['context_summary', 'updated_at'])
    
    def increment_message_count(self):
        """Increment message count and update last message timestamp."""
        self.message_count += 1
        self.last_message_at = timezone.now()
        self.save(update_fields=['message_count', 'last_message_at'])


class ChatMessage(models.Model):
    """
    Model representing individual messages in a chat.
    Stores both user and AI messages with full content.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField(help_text="Full message content")
    summary = models.TextField(
        blank=True,
        null=True,
        help_text="AI-generated summary of this message (optional)"
    )
    tokens_used = models.IntegerField(
        default=0,
        help_text="Approximate token count for this message"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat', 'created_at']),
            models.Index(fields=['chat', 'role']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.role}: {content_preview}"
    
    def estimate_tokens(self):
        """Estimate token count (rough approximation: ~4 chars per token)."""
        self.tokens_used = len(self.content) // 4
        return self.tokens_used
