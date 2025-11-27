"""
Serializers for note operations.
"""
from rest_framework import serializers
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    """
    Main serializer for Note model.
    """
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Note
        fields = ('id', 'user', 'title', 'content', 'summary', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'summary', 'created_at', 'updated_at')


class NoteCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notes with optional auto-summarization.
    """
    auto_summarize = serializers.BooleanField(default=True, write_only=True)
    
    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'auto_summarize', 'summary', 'created_at')
        read_only_fields = ('id', 'summary', 'created_at')
    
    def validate_title(self, value):
        """
        Validate that title is not empty.
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Title cannot be empty")
        return value
    
    def validate_content(self, value):
        """
        Validate that content is not empty.
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Content cannot be empty")
        return value


class NoteSummarySerializer(serializers.Serializer):
    """
    Serializer for summary generation response.
    """
    summary = serializers.CharField()
    model = serializers.CharField(read_only=True, default='gemini-1.5-flash')
