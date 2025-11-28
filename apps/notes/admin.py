"""
Admin configuration for notes app.
"""
from django.contrib import admin # type: ignore
from .models import Note, Tag, Chat, ChatMessage


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin interface for Tag model.
    """
    list_display = ('name', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('name',)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """
    Admin interface for Note model.
    """
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'tags')
    search_fields = ('title', 'content', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags',)
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


class ChatMessageInline(admin.TabularInline):
    """
    Inline admin for chat messages.
    """
    model = ChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'tokens_used', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """
    Admin interface for Chat model.
    """
    list_display = ('title', 'user', 'message_count', 'last_message_at', 'created_at')
    list_filter = ('created_at', 'updated_at', 'last_message_at')
    search_fields = ('title', 'summary', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'last_message_at', 'message_count')
    inlines = [ChatMessageInline]
    ordering = ('-last_message_at', '-created_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'message_count')
        }),
        ('Summaries', {
            'fields': ('summary', 'context_summary'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_message_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for ChatMessage model.
    """
    list_display = ('chat', 'role', 'content_preview', 'tokens_used', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'chat__title', 'chat__user__username')
    readonly_fields = ('created_at', 'tokens_used')
    ordering = ('-created_at',)
    
    def content_preview(self, obj):
        """Show preview of message content."""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(chat__user=request.user)
