"""
Chat service for managing AI conversations with context and summarization.
"""
import logging
from typing import List, Dict, Optional
from django.db import transaction # type: ignore
from django.utils import timezone # type: ignore
from apps.notes.models import Chat, ChatMessage
from apps.notes.services.gemini_service import GeminiSummarizer
from core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


class ChatService:
    """
    Service for managing chat conversations with AI context and summarization.
    """
    
    def __init__(self):
        self.ai_service = GeminiSummarizer()
        self.max_context_messages = 20  # Last N messages to keep in context
        self.summarize_threshold = 10   # Summarize after N messages
    
    def create_chat(self, user, title: str = "") -> Chat:
        """
        Create a new chat for the user.
        """
        chat = Chat.objects.create(
            user=user,
            title=title or f"Chat {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        )
        logger.info(f"Created new chat {chat.id} for user {user.username}")
        return chat
    
    @transaction.atomic
    def add_message(
        self,
        chat: Chat,
        role: str,
        content: str,
        auto_summarize: bool = True
    ) -> ChatMessage:
        """
        Add a message to the chat and optionally trigger summarization.
        
        Args:
            chat: The chat instance
            role: 'user', 'assistant', or 'system'
            content: Message content
            auto_summarize: Whether to auto-summarize after threshold
            
        Returns:
            Created ChatMessage instance
        """
        # Create the message
        message = ChatMessage.objects.create(
            chat=chat,
            role=role,
            content=content
        )
        message.estimate_tokens()
        message.save(update_fields=['tokens_used'])
        
        # Update chat metadata
        chat.increment_message_count()
        
        # Auto-summarize if threshold reached
        if auto_summarize and chat.message_count % self.summarize_threshold == 0:
            self.update_chat_summary(chat)
        
        logger.info(f"Added {role} message to chat {chat.id}")
        return message
    
    def get_chat_context(self, chat: Chat, include_summary: bool = True) -> List[Dict]:
        """
        Get the full context for AI, including recent messages and summaries.
        
        Args:
            chat: The chat instance
            include_summary: Whether to include chat summary as context
            
        Returns:
            List of message dictionaries for AI context
        """
        context = []
        
        # Add chat summary as system context if available
        if include_summary and chat.context_summary:
            context.append({
                'role': 'system',
                'content': f"Previous conversation summary: {chat.context_summary}"
            })
        
        # Get recent messages
        recent_messages = chat.messages.order_by('created_at')[:self.max_context_messages]
        
        for msg in recent_messages:
            context.append({
                'role': msg.role,
                'content': msg.content
            })
        
        return context
    
    def get_full_chat_history(self, chat: Chat) -> List[Dict]:
        """
        Get the complete chat history (all messages).
        
        Returns:
            List of all messages with metadata
        """
        messages = chat.messages.all()
        return [
            {
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'summary': msg.summary,
                'tokens_used': msg.tokens_used,
                'created_at': msg.created_at.isoformat()
            }
            for msg in messages
        ]
    
    def update_chat_summary(self, chat: Chat) -> str:
        """
        Generate and update the chat summary using AI.
        
        Returns:
            The generated summary
        """
        try:
            # Get all messages
            messages = chat.messages.all()
            
            if not messages:
                return ""
            
            # Build conversation text
            conversation = self._build_conversation_text(messages)
            
            # Generate summary
            prompt = f"""Summarize this entire conversation between a user and an AI assistant.
Capture the key topics discussed, important information shared, and the overall context.
Keep it concise but informative (around 200-300 words).

Conversation:
{conversation}

Summary:"""
            
            summary = self.ai_service._call_gemini_api(prompt)
            
            # Update chat
            chat.update_summary(summary)
            
            # Also update context summary (shorter version for AI)
            context_summary = self._generate_context_summary(messages, summary)
            chat.update_context(context_summary)
            
            logger.info(f"Updated summary for chat {chat.id}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to update chat summary: {str(e)}", exc_info=True)
            raise AIServiceException(
                "Failed to generate chat summary",
                details=str(e)
            )
    
    def summarize_message(self, message: ChatMessage) -> str:
        """
        Generate a summary for a single message.
        
        Returns:
            The generated summary
        """
        try:
            summary = self.ai_service.generate_summary(
                message.content,
                max_length=50
            )
            message.summary = summary
            message.save(update_fields=['summary'])
            return summary
            
        except Exception as e:
            logger.error(f"Failed to summarize message: {str(e)}", exc_info=True)
            return ""
    
    def get_ai_response(
        self,
        chat: Chat,
        user_message: str,
        use_context: bool = True
    ) -> str:
        """
        Get AI response for a user message, using full chat context.
        
        Args:
            chat: The chat instance
            user_message: The user's message
            use_context: Whether to include chat history as context
            
        Returns:
            AI-generated response
        """
        try:
            # Add user message
            self.add_message(chat, 'user', user_message, auto_summarize=False)
            
            # Build context
            if use_context:
                context = self.get_chat_context(chat)
                context.append({'role': 'user', 'content': user_message})
            else:
                context = [{'role': 'user', 'content': user_message}]
            
            # Build prompt with full context
            prompt = self._build_chat_prompt(context)
            
            # Get AI response
            response = self.ai_service._call_gemini_api(prompt)
            
            # Add assistant message
            self.add_message(chat, 'assistant', response)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get AI response: {str(e)}", exc_info=True)
            raise AIServiceException(
                "Failed to generate AI response",
                details=str(e)
            )
    
    def _build_conversation_text(self, messages) -> str:
        """Build a text representation of the conversation."""
        lines = []
        for msg in messages:
            role_label = msg.role.upper()
            lines.append(f"{role_label}: {msg.content}")
        return "\n\n".join(lines)
    
    def _generate_context_summary(self, messages, full_summary: str) -> str:
        """
        Generate a condensed context summary for AI.
        This is shorter than the full summary, optimized for AI context.
        """
        try:
            prompt = f"""Create a very concise context summary (max 100 words) from this conversation summary.
Focus on key facts, topics, and user preferences that would be useful for continuing the conversation.

Full Summary:
{full_summary}

Concise Context:"""
            
            context = self.ai_service._call_gemini_api(prompt)
            return context
            
        except Exception as e:
            logger.warning(f"Failed to generate context summary: {str(e)}")
            # Fallback: use truncated full summary
            return full_summary[:500]
    
    def _build_chat_prompt(self, context: List[Dict]) -> str:
        """Build a prompt with full conversation context."""
        prompt_parts = ["You are a helpful AI assistant. Here is the conversation:\n"]
        
        for msg in context:
            role = msg['role'].upper()
            content = msg['content']
            prompt_parts.append(f"{role}: {content}\n")
        
        prompt_parts.append("\nASSISTANT:")
        return "\n".join(prompt_parts)
    
    def search_chats(self, user, query: str) -> List[Chat]:
        """
        Search chats by content, title, or summary.
        """
        from django.db.models import Q # type: ignore
        
        chats = Chat.objects.filter(
            Q(user=user) &
            (
                Q(title__icontains=query) |
                Q(summary__icontains=query) |
                Q(messages__content__icontains=query)
            )
        ).distinct()
        
        return list(chats)
    
    def get_chat_statistics(self, chat: Chat) -> Dict:
        """
        Get statistics about a chat.
        """
        messages = chat.messages.all()
        
        total_tokens = sum(msg.tokens_used for msg in messages)
        user_messages = messages.filter(role='user').count()
        assistant_messages = messages.filter(role='assistant').count()
        
        return {
            'total_messages': chat.message_count,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'total_tokens': total_tokens,
            'created_at': chat.created_at.isoformat(),
            'updated_at': chat.updated_at.isoformat(),
            'last_message_at': chat.last_message_at.isoformat() if chat.last_message_at else None,
        }
