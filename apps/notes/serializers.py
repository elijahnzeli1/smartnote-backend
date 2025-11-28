"""
Serializers for note operations.
"""
from rest_framework import serializers # type: ignore
from .models import Note, Tag, Chat, ChatMessage


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model.
    """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'created_at')
        read_only_fields = ('id', 'created_at')


class NoteSerializer(serializers.ModelSerializer):
    """
    Main serializer for Note model.
    """
    user = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Tag.objects.all(), 
        write_only=True, 
        required=False,
        source='tags'
    )
    
    class Meta:
        model = Note
        fields = ('id', 'user', 'title', 'content', 'summary', 'tags', 'tag_ids', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'summary', 'created_at', 'updated_at')


class NoteCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notes with optional auto-summarization.
    """
    auto_summarize = serializers.BooleanField(default=True, write_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Tag.objects.all(), 
        write_only=True, 
        required=False,
        source='tags'
    )
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'auto_summarize', 'tags', 'tag_ids', 'summary', 'created_at')
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


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for individual chat messages.
    """
    class Meta:
        model = ChatMessage
        fields = ('id', 'role', 'content', 'summary', 'tokens_used', 'created_at')
        read_only_fields = ('id', 'summary', 'tokens_used', 'created_at')


class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer for Chat model with message count.
    """
    user = serializers.StringRelatedField(read_only=True)
    message_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Chat
        fields = (
            'id', 'user', 'title', 'summary', 'context_summary',
            'message_count', 'created_at', 'updated_at', 'last_message_at'
        )
        read_only_fields = (
            'id', 'user', 'summary', 'context_summary',
            'message_count', 'created_at', 'updated_at', 'last_message_at'
        )


class ChatDetailSerializer(serializers.ModelSerializer):
    """
    Detailed chat serializer with all messages.
    """
    user = serializers.StringRelatedField(read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Chat
        fields = (
            'id', 'user', 'title', 'summary', 'context_summary',
            'messages', 'message_count', 'created_at', 'updated_at', 'last_message_at'
        )
        read_only_fields = (
            'id', 'user', 'summary', 'context_summary',
            'message_count', 'created_at', 'updated_at', 'last_message_at'
        )


class ChatCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new chat.
    """
    class Meta:
        model = Chat
        fields = ('id', 'title', 'created_at')
        read_only_fields = ('id', 'created_at')


class MessageCreateSerializer(serializers.Serializer):
    """
    Serializer for adding a message to a chat.
    """
    content = serializers.CharField()
    role = serializers.ChoiceField(
        choices=['user', 'assistant', 'system'],
        default='user'
    )
    
    def validate_content(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Message content cannot be empty")
        return value


class ChatAIRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting an AI response.
    """
    message = serializers.CharField()
    use_context = serializers.BooleanField(default=True)
    
    def validate_message(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Message cannot be empty")
        return value


class ChatAIResponseSerializer(serializers.Serializer):
    """
    Serializer for AI response.
    """
    response = serializers.CharField()
    chat_id = serializers.IntegerField()
    message_count = serializers.IntegerField()
