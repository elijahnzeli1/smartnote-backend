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
from .models import Note, Tag
from .serializers import NoteSerializer, NoteCreateSerializer, NoteSummarySerializer, TagSerializer
from .services.gemini_service import get_summarizer
from core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tags.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializer
    
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
