"""
Views for note operations.
"""
import logging
import csv
import json
from io import StringIO
from rest_framework import viewsets, status # type: ignore
from rest_framework.decorators import action # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from django.http import HttpResponse # type: ignore
from django.db.models import Q # type: ignore
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter # type: ignore
from drf_spectacular.types import OpenApiTypes # type: ignore
from .models import Note, Tag, Chat, ChatMessage
from .serializers import (
    NoteSerializer, NoteCreateSerializer, NoteSummarySerializer, TagSerializer,
    ChatSerializer, ChatDetailSerializer, ChatCreateSerializer,
    MessageCreateSerializer, ChatAIRequestSerializer, ChatAIResponseSerializer,
    ChatMessageSerializer
)
from .services.gemini_service import get_summarizer
from .services.chat_service import ChatService
from core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List all tags",
        description="Get all tags for the authenticated user"
    ),
    retrieve=extend_schema(
        summary="Get tag details",
        description="Retrieve a specific tag by ID",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Tag ID'
            )
        ]
    ),
    create=extend_schema(
        summary="Create tag",
        description="Create a new tag for the authenticated user"
    ),
    update=extend_schema(
        summary="Update tag",
        description="Update an existing tag",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Tag ID'
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Partially update tag",
        description="Partially update an existing tag",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Tag ID'
            )
        ]
    ),
    destroy=extend_schema(
        summary="Delete tag",
        description="Delete a tag",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Tag ID'
            )
        ]
    )
)
class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tags.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()  # Base queryset, filtered in get_queryset()
    
    def get_queryset(self):
        """
        Return tags for the current user only.
        """
        return Tag.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Create a new tag for the current user.
        """
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(
        summary="List all notes",
        description="Get all notes for the authenticated user with optional search and filtering",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search notes by title or content',
                required=False
            ),
            OpenApiParameter(
                name='tag',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter notes by tag ID',
                required=False
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Get note details",
        description="Retrieve a specific note by ID",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Note ID'
            )
        ]
    ),
    create=extend_schema(
        summary="Create note",
        description="Create a new note with optional AI summarization"
    ),
    update=extend_schema(
        summary="Update note",
        description="Update an existing note",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Note ID'
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Partially update note",
        description="Partially update an existing note",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Note ID'
            )
        ]
    ),
    destroy=extend_schema(
        summary="Delete note",
        description="Delete a note",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Note ID'
            )
        ]
    )
)
class NoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notes with CRUD operations and AI summarization.
    """
    permission_classes = [IsAuthenticated]
    queryset = Note.objects.all()  # Base queryset, filtered in get_queryset()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        """
        if self.action == 'create':
            return NoteCreateSerializer
        return NoteSerializer
    
    def get_queryset(self):
        """
        Return notes for the current user only.
        Supports optional search and tag filtering.
        """
        queryset = Note.objects.filter(user=self.request.user).prefetch_related('tags')
        
        # Optional search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        # Optional tag filtering
        tag_id = self.request.query_params.get('tag', None)
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Create a new note and optionally generate summary.
        """
        auto_summarize = serializer.validated_data.pop('auto_summarize', True)
        # Extract tags before saving (ManyToMany fields need special handling)
        tags_data = serializer.validated_data.pop('tags', [])
        
        # Create the note
        note = serializer.save(user=self.request.user)
        
        # Now set the tags (ManyToMany relationship requires instance to exist first)
        if tags_data:
            note.tags.set(tags_data)
        
        if auto_summarize:
            try:
                logger.info(f"Auto-generating summary for note {note.id}")
                summarizer = get_summarizer()
                note.summary = summarizer.generate_summary(note.content)
                note.save()
                logger.info(f"Summary generated for note {note.id}")
            except AIServiceException as e:
                logger.warning(f"Failed to auto-summarize note {note.id}: {e.message}")
                # Don't fail the request, just log the error
    
    def perform_update(self, serializer):
        """
        Update a note. Clear summary if content changes.
        """
        note = self.get_object()
        old_content = note.content
        
        # Extract tags if present
        tags_data = serializer.validated_data.pop('tags', None)
        
        # Save the updated note
        note = serializer.save()
        
        # Update tags if provided
        if tags_data is not None:
            note.tags.set(tags_data)
        
        # If content changed, clear the old summary
        if old_content != note.content:
            note.summary = None
            note.save()
            logger.info(f"Content changed for note {note.id}, summary cleared")
    
    @extend_schema(
        summary="Generate AI summary",
        description="Generate or regenerate AI summary for a note using Gemini AI",
        request=None,
        responses={200: NoteSummarySerializer},
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Note ID'
            )
        ]
    )
    @action(detail=True, methods=['post'])
    def summarize(self, request, pk=None):
        """
        Generate or regenerate AI summary for a note.
        
        POST /notes/{id}/summarize/
        
        Optional body parameters:
        - method: 'abstractive' (default) or 'extractive'
        """
        note = self.get_object()
        
        try:
            summarizer = get_summarizer()
            summary = summarizer.generate_summary(note.content)
            
            # Save the summary
            note.summary = summary
            note.save()
            
            logger.info(f"Summary generated for note {note.id}")
            
            serializer = NoteSummarySerializer({
                'summary': summary,
                'model': 'gemini-1.5-flash'
            })
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except AIServiceException as e:
            logger.error(f"Failed to generate summary for note {note.id}: {e.message}")
            return Response(
                {
                    'error': 'Summary generation failed',
                    'message': e.message,
                    'details': e.details
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Unexpected error generating summary: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Internal server error',
                    'message': 'An unexpected error occurred'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Export notes",
        description="Export notes in JSON, CSV, or Markdown format with optional filtering",
        parameters=[
            OpenApiParameter(
                name='format',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Export format: json, csv, or markdown',
                required=False,
                default='json'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query to filter notes',
                required=False
            ),
            OpenApiParameter(
                name='tag',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by tag ID',
                required=False
            )
        ],
        responses={
            200: {
                'description': 'Exported notes file',
                'content': {
                    'application/json': {},
                    'text/csv': {},
                    'text/markdown': {}
                }
            }
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export notes in various formats.
        
        GET /notes/export/?format=json|csv|markdown
        
        Query parameters:
        - format: Export format (json, csv, markdown). Default: json
        - search: Optional search query to filter notes
        - tag: Optional tag ID to filter notes
        """
        export_format = request.query_params.get('format', 'json').lower()
        
        # Get filtered notes
        notes = self.get_queryset()
        
        if export_format == 'json':
            return self._export_json(notes)
        elif export_format == 'csv':
            return self._export_csv(notes)
        elif export_format == 'markdown':
            return self._export_markdown(notes)
        else:
            return Response(
                {'error': 'Invalid format. Use json, csv, or markdown.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _export_json(self, notes):
        """Export notes as JSON."""
        serializer = NoteSerializer(notes, many=True)
        response = HttpResponse(
            json.dumps(serializer.data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="notes_export.json"'
        return response
    
    def _export_csv(self, notes):
        """Export notes as CSV."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Title', 'Content', 'Summary', 'Tags', 'Created At', 'Updated At'])
        
        # Write data
        for note in notes:
            tags = ', '.join([tag.name for tag in note.tags.all()])
            writer.writerow([
                note.id,
                note.title,
                note.content,
                note.summary or '',
                tags,
                note.created_at.isoformat(),
                note.updated_at.isoformat()
            ])
        
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="notes_export.csv"'
        return response
    
    def _export_markdown(self, notes):
        """Export notes as Markdown."""
        output = StringIO()
        
        output.write("# My Notes Export\n\n")
        output.write(f"Total notes: {notes.count()}\n\n")
        output.write("---\n\n")
        
        for note in notes:
            output.write(f"## {note.title}\n\n")
            output.write(f"**Created:** {note.created_at.strftime('%Y-%m-%d %H:%M')}\n\n")
            
            if note.tags.exists():
                tags = ', '.join([f"`{tag.name}`" for tag in note.tags.all()])
                output.write(f"**Tags:** {tags}\n\n")
            
            output.write(f"{note.content}\n\n")
            
            if note.summary:
                output.write(f"### Summary\n\n")
                output.write(f"*{note.summary}*\n\n")
            
            output.write("---\n\n")
        
        response = HttpResponse(output.getvalue(), content_type='text/markdown')
        response['Content-Disposition'] = 'attachment; filename="notes_export.md"'
        return response


@extend_schema_view(
    list=extend_schema(
        summary="List all chats",
        description="Get all chats for the authenticated user with optional search",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search chats by title, summary, or message content',
                required=False
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Get chat details",
        description="Retrieve a specific chat with all messages",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Chat ID'
            )
        ]
    ),
    create=extend_schema(
        summary="Create chat",
        description="Create a new chat conversation"
    ),
    update=extend_schema(
        summary="Update chat",
        description="Update chat title or other properties",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Chat ID'
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Partially update chat",
        description="Partially update a chat",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Chat ID'
            )
        ]
    ),
    destroy=extend_schema(
        summary="Delete chat",
        description="Delete a chat and all its messages",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Chat ID'
            )
        ]
    )
)
class ChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat conversations with AI context.
    """
    permission_classes = [IsAuthenticated]
    queryset = Chat.objects.all()  # Base queryset, filtered in get_queryset()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_service = ChatService()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return ChatDetailSerializer
        elif self.action == 'create':
            return ChatCreateSerializer
        return ChatSerializer
    
    def get_queryset(self):
        """Return chats for the current user only."""
        queryset = Chat.objects.filter(user=self.request.user)
        
        # Optional search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(summary__icontains=search) |
                Q(messages__content__icontains=search)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        """Create a new chat."""
        title = serializer.validated_data.get('title', '')
        chat = self.chat_service.create_chat(self.request.user, title)
        serializer.instance = chat
    
    @extend_schema(
        summary="Add message to chat",
        description="Add a message to the chat manually (without AI response)",
        request=MessageCreateSerializer,
        responses={201: ChatMessageSerializer},
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Chat ID'
            )
        ]
    )
    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """
        Add a message to the chat.
        POST /api/chats/{id}/add_message/
        Body: {"content": "message text", "role": "user"}
        """
        chat = self.get_object()
        serializer = MessageCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            message = self.chat_service.add_message(
                chat=chat,
                role=serializer.validated_data['role'],
                content=serializer.validated_data['content']
            )
            
            return Response(
                ChatMessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Get AI response",
        description="Send a message and get AI response with full conversation context",
        request=ChatAIRequestSerializer,
        responses={200: ChatAIResponseSerializer},
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Chat ID'
            )
        ]
    )
    @action(detail=True, methods=['post'])
    def ai_response(self, request, pk=None):
        """
        Send a message and get AI response with full context.
        POST /api/chats/{id}/ai_response/
        Body: {"message": "user message", "use_context": true}
        """
        chat = self.get_object()
        serializer = ChatAIRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                response = self.chat_service.get_ai_response(
                    chat=chat,
                    user_message=serializer.validated_data['message'],
                    use_context=serializer.validated_data.get('use_context', True)
                )
                
                # Refresh chat to get updated count
                chat.refresh_from_db()
                
                return Response(
                    ChatAIResponseSerializer({
                        'response': response,
                        'chat_id': chat.id,
                        'message_count': chat.message_count
                    }).data,
                    status=status.HTTP_200_OK
                )
                
            except AIServiceException as e:
                logger.error(f"AI response error: {e.message}")
                return Response(
                    {'error': e.message, 'details': e.details},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Update chat summary",
        description="Generate or update AI summary for the entire chat conversation",
        request=None,
        responses={200: ChatDetailSerializer},
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Chat ID'
            )
        ]
    )
    @action(detail=True, methods=['post'])
    def update_summary(self, request, pk=None):
        """
        Generate/update the chat summary using AI.
        POST /api/chats/{id}/update_summary/
        """
        chat = self.get_object()
        
        try:
            summary = self.chat_service.update_chat_summary(chat)
            chat.refresh_from_db()
            
            return Response(
                ChatDetailSerializer(chat).data,
                status=status.HTTP_200_OK
            )
            
        except AIServiceException as e:
            logger.error(f"Summary generation error: {e.message}")
            return Response(
                {'error': e.message, 'details': e.details},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @extend_schema(
        summary="Get chat context",
        description="Get the full context for AI (recent messages + summary)",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Chat ID'
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def context(self, request, pk=None):
        """
        Get the full context for AI (recent messages + summary).
        GET /api/chats/{id}/context/
        """
        chat = self.get_object()
        context = self.chat_service.get_chat_context(chat)
        
        return Response({
            'chat_id': chat.id,
            'context': context,
            'summary': chat.context_summary
        })
    
    @extend_schema(
        summary="Get chat history",
        description="Get the complete chat history with all messages",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Chat ID'
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Get the complete chat history (all messages).
        GET /api/chats/{id}/history/
        """
        chat = self.get_object()
        history = self.chat_service.get_full_chat_history(chat)
        
        return Response({
            'chat_id': chat.id,
            'title': chat.title,
            'message_count': chat.message_count,
            'messages': history
        })
    
    @extend_schema(
        summary="Get chat statistics",
        description="Get statistics about the chat (message counts, tokens, timestamps)",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Chat ID'
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get chat statistics (message counts, tokens, etc.).
        GET /api/chats/{id}/statistics/
        """
        chat = self.get_object()
        stats = self.chat_service.get_chat_statistics(chat)
        
        return Response(stats)
    
    @extend_schema(
        summary="Search chats",
        description="Search chats by content, title, or summary",
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query',
                required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search chats by content.
        GET /api/chats/search/?q=query
        """
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {'error': 'Query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        chats = self.chat_service.search_chats(request.user, query)
        serializer = ChatSerializer(chats, many=True)
        
        return Response({
            'query': query,
            'count': len(chats),
            'results': serializer.data
        })
