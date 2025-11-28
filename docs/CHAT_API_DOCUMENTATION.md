# Chat API Documentation

## Overview
The Chat API provides full conversational AI capabilities with context management, automatic summarization, and complete message history storage.

## Key Features
- ✅ **Full Message Storage** - All user and AI messages stored in database
- ✅ **AI Context Management** - AI has access to entire conversation history
- ✅ **Automatic Summarization** - Chat summaries generated periodically
- ✅ **Context Summaries** - Condensed context for efficient AI processing
- ✅ **Search & Retrieval** - Search across all chats and messages
- ✅ **Statistics** - Track message counts, tokens, and timestamps

## Models

### Chat
Represents a conversation with AI.

```python
{
    "id": 1,
    "user": "username",
    "title": "Chat Title",
    "summary": "AI-generated conversation summary",
    "context_summary": "Condensed context for AI",
    "message_count": 15,
    "created_at": "2025-11-27T10:00:00Z",
    "updated_at": "2025-11-27T12:00:00Z",
    "last_message_at": "2025-11-27T12:00:00Z"
}
```

### ChatMessage
Individual messages in a chat.

```python
{
    "id": 1,
    "role": "user",  // or "assistant", "system"
    "content": "Full message content",
    "summary": "AI summary of this message (optional)",
    "tokens_used": 50,
    "created_at": "2025-11-27T10:00:00Z"
}
```

## API Endpoints

### 1. List Chats
Get all chats for the authenticated user.

```http
GET /api/chats/
```

**Query Parameters:**
- `search` (optional): Search chats by title, summary, or message content

**Response:**
```json
[
    {
        "id": 1,
        "user": "username",
        "title": "My Chat",
        "summary": "Conversation about...",
        "message_count": 10,
        "created_at": "2025-11-27T10:00:00Z",
        "updated_at": "2025-11-27T12:00:00Z",
        "last_message_at": "2025-11-27T12:00:00Z"
    }
]
```

### 2. Create Chat
Create a new chat conversation.

```http
POST /api/chats/
Content-Type: application/json

{
    "title": "My New Chat"
}
```

**Response:**
```json
{
    "id": 2,
    "title": "My New Chat",
    "created_at": "2025-11-27T13:00:00Z"
}
```

### 3. Get Chat Details
Get a specific chat with all messages.

```http
GET /api/chats/{id}/
```

**Response:**
```json
{
    "id": 1,
    "user": "username",
    "title": "My Chat",
    "summary": "Full conversation summary...",
    "context_summary": "Key context points...",
    "message_count": 10,
    "messages": [
        {
            "id": 1,
            "role": "user",
            "content": "Hello!",
            "tokens_used": 10,
            "created_at": "2025-11-27T10:00:00Z"
        },
        {
            "id": 2,
            "role": "assistant",
            "content": "Hi! How can I help you?",
            "tokens_used": 15,
            "created_at": "2025-11-27T10:01:00Z"
        }
    ],
    "created_at": "2025-11-27T10:00:00Z",
    "updated_at": "2025-11-27T12:00:00Z",
    "last_message_at": "2025-11-27T12:00:00Z"
}
```

### 4. Add Message to Chat
Add a message without AI response (for manual entry).

```http
POST /api/chats/{id}/add_message/
Content-Type: application/json

{
    "content": "This is my message",
    "role": "user"  // or "assistant", "system"
}
```

**Response:**
```json
{
    "id": 3,
    "role": "user",
    "content": "This is my message",
    "tokens_used": 20,
    "created_at": "2025-11-27T13:00:00Z"
}
```

### 5. Get AI Response (Main Chat Endpoint)
Send a message and get AI response with full context.

```http
POST /api/chats/{id}/ai_response/
Content-Type: application/json

{
    "message": "What did we discuss earlier?",
    "use_context": true
}
```

**How It Works:**
1. Your message is stored in the database
2. AI gets the full conversation context (including summaries)
3. AI generates a contextual response
4. AI response is stored in the database
5. Both messages are returned

**Response:**
```json
{
    "response": "Earlier we discussed...",
    "chat_id": 1,
    "message_count": 12
}
```

### 6. Update Chat Summary
Generate/update the AI summary for the entire conversation.

```http
POST /api/chats/{id}/update_summary/
```

**Response:**
```json
{
    "id": 1,
    "user": "username",
    "title": "My Chat",
    "summary": "This conversation covered topics A, B, and C...",
    "context_summary": "Key points: ...",
    "message_count": 10,
    "messages": [...],
    "created_at": "2025-11-27T10:00:00Z",
    "updated_at": "2025-11-27T13:00:00Z",
    "last_message_at": "2025-11-27T12:00:00Z"
}
```

### 7. Get Chat Context
Get the context that will be sent to AI (recent messages + summary).

```http
GET /api/chats/{id}/context/
```

**Response:**
```json
{
    "chat_id": 1,
    "context": [
        {
            "role": "system",
            "content": "Previous conversation summary: ..."
        },
        {
            "role": "user",
            "content": "First message..."
        },
        {
            "role": "assistant",
            "content": "First response..."
        }
    ],
    "summary": "Condensed context for AI..."
}
```

### 8. Get Full Chat History
Get all messages in the chat (unbounded).

```http
GET /api/chats/{id}/history/
```

**Response:**
```json
{
    "chat_id": 1,
    "title": "My Chat",
    "message_count": 50,
    "messages": [
        {
            "id": 1,
            "role": "user",
            "content": "...",
            "summary": null,
            "tokens_used": 20,
            "created_at": "2025-11-27T10:00:00Z"
        },
        // ... all 50 messages
    ]
}
```

### 9. Get Chat Statistics
Get statistics about the chat.

```http
GET /api/chats/{id}/statistics/
```

**Response:**
```json
{
    "total_messages": 50,
    "user_messages": 25,
    "assistant_messages": 24,
    "total_tokens": 2500,
    "created_at": "2025-11-27T10:00:00Z",
    "updated_at": "2025-11-27T13:00:00Z",
    "last_message_at": "2025-11-27T13:00:00Z"
}
```

### 10. Search Chats
Search across all chats and messages.

```http
GET /api/chats/search/?q=python
```

**Response:**
```json
{
    "query": "python",
    "count": 3,
    "results": [
        {
            "id": 1,
            "title": "Python Tutorial",
            "summary": "Discussion about Python...",
            "message_count": 15,
            "created_at": "2025-11-27T10:00:00Z"
        }
    ]
}
```

### 11. Delete Chat
Delete a chat and all its messages.

```http
DELETE /api/chats/{id}/
```

**Response:** `204 No Content`

## Usage Examples

### Example 1: Start a New Conversation

```javascript
// 1. Create a chat
const chatResponse = await fetch('/api/chats/', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        title: 'Python Help'
    })
});
const chat = await chatResponse.json();

// 2. Send first message and get AI response
const messageResponse = await fetch(`/api/chats/${chat.id}/ai_response/`, {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        message: 'How do I create a list in Python?',
        use_context: true
    })
});
const aiResponse = await messageResponse.json();
console.log(aiResponse.response); // AI's answer
```

### Example 2: Continue Conversation with Context

```javascript
// Send another message - AI will remember previous context
const response = await fetch(`/api/chats/${chatId}/ai_response/`, {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        message: 'Can you show me an example?',
        use_context: true  // AI knows you're asking about Python lists
    })
});
```

### Example 3: Get Full Conversation History

```javascript
const history = await fetch(`/api/chats/${chatId}/history/`, {
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN'
    }
});
const data = await history.json();

// Display all messages
data.messages.forEach(msg => {
    console.log(`${msg.role}: ${msg.content}`);
});
```

### Example 4: Generate Summary

```javascript
// After 10+ messages, generate a summary
const summary = await fetch(`/api/chats/${chatId}/update_summary/`, {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN'
    }
});
const chatWithSummary = await summary.json();
console.log(chatWithSummary.summary); // AI-generated conversation summary
```

## How Context Management Works

### 1. Message Storage
Every message (user and AI) is stored in the database with:
- Full content
- Role (user/assistant/system)
- Timestamp
- Token count estimate

### 2. Context Building
When you send a message, the AI receives:
- **Context Summary**: Condensed version of older messages
- **Recent Messages**: Last 20 messages in full
- **Your Current Message**: The new message you just sent

### 3. Automatic Summarization
- Every 10 messages, a summary is automatically generated
- Summary captures key topics and important information
- Context summary is created for efficient AI processing

### 4. Full History Access
- All messages are always stored, nothing is lost
- Use `/history/` endpoint to retrieve complete conversation
- Search across all messages with `/search/` endpoint

## Best Practices

### 1. Use Context Wisely
```javascript
// For continuing conversation
{ "use_context": true }

// For standalone questions
{ "use_context": false }
```

### 2. Generate Summaries Periodically
```javascript
// After significant conversation milestones
if (messageCount % 20 === 0) {
    await updateChatSummary(chatId);
}
```

### 3. Set Descriptive Titles
```javascript
// Good
{ "title": "Python List Comprehensions Tutorial" }

// Less helpful
{ "title": "Chat 1" }
```

### 4. Search Before Creating New Chats
```javascript
// Check if similar conversation exists
const existing = await searchChats('python lists');
if (existing.count > 0) {
    // Continue existing chat
} else {
    // Create new chat
}
```

## Error Handling

### AI Service Errors
```json
{
    "error": "Failed to generate AI response",
    "details": "API quota exceeded"
}
```
**Status Code:** 503 Service Unavailable

### Validation Errors
```json
{
    "message": ["Message cannot be empty"]
}
```
**Status Code:** 400 Bad Request

### Not Found
```json
{
    "detail": "Not found."
}
```
**Status Code:** 404 Not Found

## Performance Considerations

### Token Limits
- Each message tracks approximate token usage
- Monitor total tokens to stay within limits
- Use context summary for long conversations

### Database Performance
- Messages are indexed by chat and timestamp
- Searching is optimized with full-text search
- Old chats can be archived (future feature)

### AI Response Time
- First response: ~2-5 seconds
- With context: ~3-7 seconds
- Retry logic with exponential backoff included

## Migration Guide

### From Old Note System
If you have existing notes, you can convert them to chats:

```python
# Example conversion script
from apps.notes.models import Note, Chat, ChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()

for note in Note.objects.all():
    # Create chat from note
    chat = Chat.objects.create(
        user=note.user,
        title=note.title
    )
    
    # Add note content as first message
    ChatMessage.objects.create(
        chat=chat,
        role='user',
        content=note.content
    )
    
    # Add summary as assistant message if exists
    if note.summary:
        ChatMessage.objects.create(
            chat=chat,
            role='assistant',
            content=note.summary
        )
    
    chat.increment_message_count()
    chat.increment_message_count()
```

## Security Notes

### Authentication Required
All chat endpoints require JWT authentication:
```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### User Isolation
- Users can only access their own chats
- Admin users can see all chats in admin panel
- Database queries are automatically filtered by user

### Data Privacy
- All messages stored with encryption at rest
- Transmitted over HTTPS only
- API keys stored as environment variables

## Future Enhancements

### Planned Features
- [ ] Chat export (JSON, PDF)
- [ ] Chat sharing with other users
- [ ] Message editing and deletion
- [ ] Chat folders/categorization
- [ ] Voice message support
- [ ] Image attachments
- [ ] Multi-language support
- [ ] Custom AI models per chat
- [ ] Cost tracking per chat

## Support

For issues or questions:
1. Check error messages in response
2. Review Django logs for detailed errors
3. Verify environment variables are set
4. Ensure database migrations are applied

## Database Schema

```sql
-- Chats table
CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200),
    summary TEXT,
    context_summary TEXT,
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_message_at TIMESTAMP
);

-- Chat messages table
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER REFERENCES chats(id) ON DELETE CASCADE,
    role VARCHAR(10),  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    summary TEXT,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_chats_user_last_message ON chats(user_id, last_message_at);
CREATE INDEX idx_messages_chat_created ON chat_messages(chat_id, created_at);
```

---

**API Version:** 1.0  
**Last Updated:** November 27, 2025  
**Base URL:** `/api/chats/`
