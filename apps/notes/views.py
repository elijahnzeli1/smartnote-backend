"""
Views for note operations.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Note
from .serializers import NoteSerializer, NoteCreateSerializer, NoteSummarySerializer
from .services.gemini_service import get_summarizer
from core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


class NoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notes with CRUD operations and AI summarization.
    """
    permission_classes = [IsAuthenticated]
    
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
        Supports optional search query parameter.
        """
        queryset = Note.objects.filter(user=self.request.user)
        
        # Optional search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Create a new note and optionally generate summary.
        """
        auto_summarize = serializer.validated_data.pop('auto_summarize', True)
        note = serializer.save(user=self.request.user)
        
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
        
        # Save the updated note
        note = serializer.save()
        
        # If content changed, clear the old summary
        if old_content != note.content:
            note.summary = None
            note.save()
            logger.info(f"Content changed for note {note.id}, summary cleared")
    
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
