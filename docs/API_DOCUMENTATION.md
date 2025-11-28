# Smart Notes - API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints Reference](#endpoints-reference)
4. [Request/Response Examples](#requestresponse-examples)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Postman Collection](#postman-collection)

---

## Overview

### Base URL
- **Development**: `http://localhost:8000/api`
- **Production**: `https://your-domain.com/api`

### API Version
Current version: **v1**

### Content Type
All requests and responses use JSON format:
```
Content-Type: application/json
```

### API Documentation
- **Swagger UI**: `/api/docs/`
- **OpenAPI Schema**: `/api/schema/`

---

## Authentication

### Authentication Method
Smart Notes API uses **JWT (JSON Web Token)** for authentication.

### Token Types
1. **Access Token**
   - Short-lived (15 minutes)
   - Used for API requests
   - Included in Authorization header

2. **Refresh Token**
   - Long-lived (7 days)
   - Used to obtain new access tokens
   - Stored securely by client

### Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    
    Client->>API: POST /auth/login/ (credentials)
    API->>Client: Returns access & refresh tokens
    Client->>API: GET /notes/ (with access token)
    API->>Client: Returns notes data
    Note over Client,API: Access token expires
    Client->>API: POST /auth/token/refresh/ (refresh token)
    API->>Client: Returns new access token
```

### Including Authentication Token

All authenticated requests must include the access token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

Example:
```http
GET /api/notes/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## Endpoints Reference

### Authentication Endpoints

#### Register User
Create a new user account.

**Endpoint**: `POST /api/auth/register/`

**Authentication**: Not required

**Request Body**:
```json
{
  "username": "string (required, unique)",
  "email": "string (required, unique, valid email)",
  "password": "string (required, min 8 characters)",
  "password_confirm": "string (required, must match password)"
}
```

**Response**: `201 Created`
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2025-11-27T10:00:00Z"
  },
  "message": "User registered successfully"
}
```

**Validation Rules**:
- Username: 3-150 characters, alphanumeric and underscores
- Email: Valid email format
- Password: Minimum 8 characters
- Passwords must match

---

#### Login
Authenticate and receive JWT tokens.

**Endpoint**: `POST /api/auth/login/`

**Authentication**: Not required

**Request Body**:
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response**: `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2025-11-27T10:00:00Z"
  }
}
```

**Error Response**: `401 Unauthorized`
```json
{
  "detail": "Invalid credentials"
}
```

---

#### Refresh Access Token
Obtain a new access token using refresh token.

**Endpoint**: `POST /api/auth/token/refresh/`

**Authentication**: Not required (uses refresh token)

**Request Body**:
```json
{
  "refresh": "string (required)"
}
```

**Response**: `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

#### Get User Profile
Retrieve authenticated user's profile.

**Endpoint**: `GET /api/auth/profile/`

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2025-11-27T10:00:00Z"
}
```

---

#### Update User Profile
Update authenticated user's profile.

**Endpoint**: `PATCH /api/auth/profile/`

**Authentication**: Required

**Request Body**:
```json
{
  "email": "newemail@example.com"
}
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "newemail@example.com",
  "created_at": "2025-11-27T10:00:00Z"
}
```

---

### Notes Endpoints

#### List Notes
Retrieve all notes for authenticated user with optional filtering.

**Endpoint**: `GET /api/notes/`

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search in title and content |
| `tag` | integer | Filter by tag ID |
| `page` | integer | Page number (default: 1) |

**Example Requests**:
```http
GET /api/notes/
GET /api/notes/?search=meeting
GET /api/notes/?tag=5
GET /api/notes/?search=project&tag=3
```

**Response**: `200 OK`
```json
{
  "count": 100,
  "next": "http://api.example.com/notes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": "johndoe",
      "title": "Meeting Notes",
      "content": "Discussed project timeline and deliverables...",
      "summary": "Project meeting covering timeline and key deliverables.",
      "tags": [
        {
          "id": 1,
          "name": "work",
          "created_at": "2025-11-27T10:00:00Z"
        }
      ],
      "created_at": "2025-11-27T10:00:00Z",
      "updated_at": "2025-11-27T10:30:00Z"
    }
  ]
}
```

---

#### Create Note
Create a new note with optional auto-summarization.

**Endpoint**: `POST /api/notes/`

**Authentication**: Required

**Request Body**:
```json
{
  "title": "string (required, max 200 chars)",
  "content": "string (required)",
  "auto_summarize": "boolean (optional, default: true)",
  "tag_ids": "array of integers (optional)"
}
```

**Example**:
```json
{
  "title": "Project Planning",
  "content": "We need to finalize the project scope, assign tasks to team members, and set up weekly check-ins. The deadline is December 15th.",
  "auto_summarize": true,
  "tag_ids": [1, 3]
}
```

**Response**: `201 Created`
```json
{
  "id": 10,
  "title": "Project Planning",
  "content": "We need to finalize the project scope...",
  "summary": "Project requires scope finalization, task assignment, and weekly check-ins before December 15th deadline.",
  "tags": [
    {
      "id": 1,
      "name": "work",
      "created_at": "2025-11-27T10:00:00Z"
    },
    {
      "id": 3,
      "name": "planning",
      "created_at": "2025-11-27T10:00:00Z"
    }
  ],
  "created_at": "2025-11-27T11:00:00Z"
}
```

---

#### Get Note
Retrieve a specific note by ID.

**Endpoint**: `GET /api/notes/{id}/`

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Note ID |

**Response**: `200 OK`
```json
{
  "id": 10,
  "user": "johndoe",
  "title": "Project Planning",
  "content": "We need to finalize the project scope...",
  "summary": "Project requires scope finalization...",
  "tags": [...],
  "created_at": "2025-11-27T11:00:00Z",
  "updated_at": "2025-11-27T11:00:00Z"
}
```

**Error Response**: `404 Not Found`
```json
{
  "detail": "Not found."
}
```

---

#### Update Note
Update an existing note (full update).

**Endpoint**: `PUT /api/notes/{id}/`

**Authentication**: Required

**Request Body**:
```json
{
  "title": "string (required)",
  "content": "string (required)",
  "tag_ids": "array of integers (optional)"
}
```

**Note**: When content is updated, the summary is automatically cleared and needs to be regenerated.

**Response**: `200 OK`
```json
{
  "id": 10,
  "title": "Updated Title",
  "content": "Updated content...",
  "summary": null,
  "tags": [...],
  "created_at": "2025-11-27T11:00:00Z",
  "updated_at": "2025-11-27T11:15:00Z"
}
```

---

#### Partial Update Note
Update specific fields of a note.

**Endpoint**: `PATCH /api/notes/{id}/`

**Authentication**: Required

**Request Body** (all fields optional):
```json
{
  "title": "string",
  "content": "string",
  "tag_ids": "array of integers"
}
```

**Example**:
```json
{
  "tag_ids": [1, 2, 5]
}
```

**Response**: `200 OK`

---

#### Delete Note
Delete a note permanently.

**Endpoint**: `DELETE /api/notes/{id}/`

**Authentication**: Required

**Response**: `204 No Content`

---

#### Generate Summary
Generate or regenerate AI summary for a note.

**Endpoint**: `POST /api/notes/{id}/summarize/`

**Authentication**: Required

**Request Body**: None required

**Response**: `200 OK`
```json
{
  "summary": "This is the AI-generated summary of the note content.",
  "model": "gemini-1.5-flash"
}
```

**Error Response**: `503 Service Unavailable`
```json
{
  "error": "Summary generation failed",
  "message": "AI service temporarily unavailable",
  "details": "Rate limit exceeded"
}
```

**Use Cases**:
- Regenerate summary after content changes
- Generate summary for notes created without auto-summarization
- Update summary with latest AI model

---

#### Export Notes
Export notes in various formats.

**Endpoint**: `GET /api/notes/export/`

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | Export format: `json`, `csv`, or `markdown` (default: json) |
| `search` | string | Filter notes by search query |
| `tag` | integer | Filter notes by tag ID |

**Example Requests**:
```http
GET /api/notes/export/?format=json
GET /api/notes/export/?format=csv&search=important
GET /api/notes/export/?format=markdown&tag=3
```

**Response**: File download

**JSON Format** (`application/json`):
```json
[
  {
    "id": 1,
    "user": "johndoe",
    "title": "Note Title",
    "content": "Note content...",
    "summary": "Summary...",
    "tags": [...],
    "created_at": "2025-11-27T10:00:00Z",
    "updated_at": "2025-11-27T10:00:00Z"
  }
]
```

**CSV Format** (`text/csv`):
```csv
ID,Title,Content,Summary,Tags,Created At,Updated At
1,Note Title,Note content...,Summary...,work,2025-11-27T10:00:00Z,2025-11-27T10:00:00Z
```

**Markdown Format** (`text/markdown`):
```markdown
# My Notes Export

Total notes: 10

---

## Note Title

**Created:** 2025-11-27 10:00

**Tags:** `work`, `important`

Note content goes here...

### Summary

*AI-generated summary of the note.*

---
```

---

### Tags Endpoints

#### List Tags
Retrieve all tags for authenticated user.

**Endpoint**: `GET /api/tags/`

**Authentication**: Required

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "name": "work",
    "created_at": "2025-11-27T10:00:00Z"
  },
  {
    "id": 2,
    "name": "personal",
    "created_at": "2025-11-27T10:00:00Z"
  }
]
```

---

#### Create Tag
Create a new tag.

**Endpoint**: `POST /api/tags/`

**Authentication**: Required

**Request Body**:
```json
{
  "name": "string (required, max 50 chars, unique per user)"
}
```

**Response**: `201 Created`
```json
{
  "id": 5,
  "name": "project",
  "created_at": "2025-11-27T11:00:00Z"
}
```

**Error Response**: `400 Bad Request`
```json
{
  "name": ["Tag with this name already exists."]
}
```

---

#### Get Tag
Retrieve a specific tag.

**Endpoint**: `GET /api/tags/{id}/`

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "id": 5,
  "name": "project",
  "created_at": "2025-11-27T11:00:00Z"
}
```

---

#### Update Tag
Update a tag name.

**Endpoint**: `PUT /api/tags/{id}/`

**Authentication**: Required

**Request Body**:
```json
{
  "name": "string (required)"
}
```

**Response**: `200 OK`

---

#### Delete Tag
Delete a tag. Notes with this tag will not be deleted, only the tag assignment is removed.

**Endpoint**: `DELETE /api/tags/{id}/`

**Authentication**: Required

**Response**: `204 No Content`

---

## Request/Response Examples

### Complete Workflow Example

#### 1. Register User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

#### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}
```

#### 3. Create Tag
```bash
curl -X POST http://localhost:8000/api/tags/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "name": "work"
  }'
```

#### 4. Create Note with Tag
```bash
curl -X POST http://localhost:8000/api/notes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "title": "Team Meeting",
    "content": "Discussed Q4 goals, budget allocation, and hiring plans. Action items: Update roadmap, schedule follow-up.",
    "auto_summarize": true,
    "tag_ids": [1]
  }'
```

#### 5. Search Notes
```bash
curl -X GET "http://localhost:8000/api/notes/?search=meeting" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

#### 6. Export Notes
```bash
curl -X GET "http://localhost:8000/api/notes/export/?format=markdown" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -o notes_export.md
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "error": "Error type",
  "message": "Human-readable error message",
  "details": "Additional error details (optional)"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | External service (AI) unavailable |

### Common Error Scenarios

#### Invalid Credentials
```json
{
  "detail": "No active account found with the given credentials"
}
```

#### Validation Error
```json
{
  "title": ["This field is required."],
  "content": ["This field may not be blank."]
}
```

#### Token Expired
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

#### AI Service Error
```json
{
  "error": "Summary generation failed",
  "message": "AI service temporarily unavailable",
  "details": "Request timeout after 30 seconds"
}
```

#### Rate Limit Exceeded
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

---

## Rate Limiting

### Default Limits

| User Type | Limit |
|-----------|-------|
| Anonymous | 100 requests/hour |
| Authenticated | 1000 requests/hour |

### Rate Limit Headers

Every response includes rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1638360000
```

### Handling Rate Limits

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response:

```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

**Best Practices**:
- Implement exponential backoff
- Cache responses when possible
- Batch operations when available
- Monitor rate limit headers

---

## Postman Collection

### Import Collection

1. Download the Postman collection:
   ```bash
   curl -o SmartNotes.postman_collection.json \
     http://localhost:8000/api/schema/?format=json
   ```

2. Import in Postman:
   - Open Postman
   - Click "Import"
   - Select the downloaded file

### Environment Variables

Set up the following environment variables in Postman:

```json
{
  "base_url": "http://localhost:8000/api",
  "access_token": "",
  "refresh_token": "",
  "user_id": ""
}
```

### Pre-request Script (Auto-token refresh)

Add this to your collection's pre-request script:

```javascript
const accessToken = pm.environment.get("access_token");
const refreshToken = pm.environment.get("refresh_token");

// Check if access token exists
if (!accessToken && refreshToken) {
    // Refresh access token
    pm.sendRequest({
        url: pm.environment.get("base_url") + "/auth/token/refresh/",
        method: 'POST',
        header: {
            'Content-Type': 'application/json'
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                refresh: refreshToken
            })
        }
    }, function (err, res) {
        if (!err) {
            const newAccessToken = res.json().access;
            pm.environment.set("access_token", newAccessToken);
        }
    });
}
```

---

## API Best Practices

### 1. Always Include Content-Type
```http
Content-Type: application/json
```

### 2. Handle Token Expiration
Implement automatic token refresh logic in your client.

### 3. Use HTTPS in Production
Never send tokens over unencrypted connections.

### 4. Validate Input
Always validate user input before sending to API.

### 5. Handle Errors Gracefully
Implement proper error handling for all API calls.

### 6. Cache When Appropriate
Cache GET requests to reduce API calls.

### 7. Paginate Large Results
Use pagination for list endpoints.

### 8. Rate Limit Aware
Monitor rate limit headers and implement backoff strategies.

---

## Changelog

### Version 1.0.0 (2025-11-27)
- Initial API release
- User authentication (register, login, profile)
- Notes CRUD operations
- AI summarization with Gemini
- Tag management
- Export functionality (JSON, CSV, Markdown)
- Search and filter capabilities

---

## Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/SmartNoteAPI/issues)
- **Documentation**: [Full Documentation](/docs)
- **Email**: support@smartnotes.com

---

**Last Updated**: November 27, 2025  
**API Version**: 1.0.0
