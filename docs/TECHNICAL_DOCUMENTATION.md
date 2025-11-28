# Smart Notes - Full Technical Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Backend Implementation](#backend-implementation)
4. [Frontend Implementation](#frontend-implementation)
5. [AI Integration](#ai-integration)
6. [Database Schema](#database-schema)
7. [API Design](#api-design)
8. [Security](#security)
9. [Testing Strategy](#testing-strategy)
10. [Performance Optimization](#performance-optimization)
11. [Error Handling](#error-handling)
12. [Development Workflow](#development-workflow)

---

## System Overview

### Purpose
Smart Notes is an AI-powered note-taking application that helps users create, organize, and intelligently summarize their notes using Google's Gemini AI.

### Key Objectives
- Provide a seamless note-taking experience
- Leverage AI to generate intelligent summaries
- Enable efficient organization with tags
- Support multiple export formats
- Ensure data security and privacy

### Target Users
- Students taking lecture notes
- Professionals documenting meetings
- Researchers collecting information
- Anyone needing organized note-taking with AI assistance

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│                  (Next.js 14 + TypeScript)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │  Notes   │  │   Tags   │  │  Export  │   │
│  │  Pages   │  │  Pages   │  │Component │  │Component │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │ HTTPS/JSON
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                       │
│                   (Django REST Framework)                    │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Authentication  │  │   Authorization  │               │
│  │    Middleware    │  │    Middleware    │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   User   │  │   Note   │  │   Tag    │  │  Gemini  │   │
│  │ Services │  │ Services │  │ Services │  │ Services │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Access Layer                       │
│                         (Django ORM)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │   User   │  │   Note   │  │   Tag    │                  │
│  │  Model   │  │  Model   │  │  Model   │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     PostgreSQL Database                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   External Services Layer                    │
│                    (Google Gemini API)                       │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **User Request Flow**
   ```
   User → Frontend → API Client → Backend API → Business Logic → Database
                                              ↓
                                       Gemini Service (if needed)
   ```

2. **Note Creation with AI Summary**
   ```
   POST /api/notes/
   ↓
   NoteViewSet.create()
   ↓
   Save Note to Database
   ↓
   GeminiService.generate_summary()
   ↓
   Update Note with Summary
   ↓
   Return Response
   ```

---

## Backend Implementation

### Django Settings Structure

The backend uses **split settings** for better organization:

```python
# settings/
#   ├── __init__.py      # Auto-detect environment
#   ├── base.py          # Common settings
#   ├── dev.py           # Development settings
#   └── prod.py          # Production settings
```

#### base.py - Common Settings
```python
# Security
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'apps.users',
    'apps.notes',
]

# Authentication
AUTH_USER_MODEL = 'users.User'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Gemini AI Settings
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
GEMINI_MAX_RETRIES = int(os.getenv('GEMINI_MAX_RETRIES', 3))
GEMINI_TIMEOUT = int(os.getenv('GEMINI_TIMEOUT', 30))
```

### Models Architecture

#### User Model
```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom user model with additional fields"""
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
```

#### Note Model
```python
# apps/notes/models.py
class Note(models.Model):
    """Note model with AI summary and tags"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField('Tag', related_name='notes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
```

#### Tag Model
```python
class Tag(models.Model):
    """Tag model for organizing notes"""
    name = models.CharField(max_length=50)
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
```

### ViewSets Implementation

#### NoteViewSet
```python
class NoteViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD operations for notes with additional features:
    - Auto-summarization on create
    - Manual summarization endpoint
    - Tag filtering
    - Search functionality
    - Export in multiple formats
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user).prefetch_related('tags')
        
        # Search
        if search := self.request.query_params.get('search'):
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        # Tag filter
        if tag_id := self.request.query_params.get('tag'):
            queryset = queryset.filter(tags__id=tag_id)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def summarize(self, request, pk=None):
        """Generate AI summary for note"""
        note = self.get_object()
        summarizer = get_summarizer()
        summary = summarizer.generate_summary(note.content)
        note.summary = summary
        note.save()
        return Response({'summary': summary})
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export notes in various formats"""
        format = request.query_params.get('format', 'json')
        notes = self.get_queryset()
        
        if format == 'json':
            return self._export_json(notes)
        elif format == 'csv':
            return self._export_csv(notes)
        elif format == 'markdown':
            return self._export_markdown(notes)
```

### Serializers Pattern

```python
# Base serializer for read operations
class NoteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), 
        write_only=True, required=False, source='tags'
    )
    
    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ('id', 'user', 'summary', 'created_at', 'updated_at')

# Specialized serializer for creation
class NoteCreateSerializer(serializers.ModelSerializer):
    auto_summarize = serializers.BooleanField(default=True, write_only=True)
    
    def validate_content(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Content cannot be empty")
        return value
```

---

## Frontend Implementation

### Next.js 14 App Router Structure

```typescript
// app/layout.tsx - Root layout
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <Navbar />
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}

// app/notes/page.tsx - Notes page
export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  
  // Load notes and tags
  useEffect(() => {
    loadNotes();
    loadTags();
  }, []);
  
  return (
    <div>
      <NoteEditor onSave={handleSaveNote} />
      <TagFilter tags={tags} onFilter={handleFilter} />
      <ExportButton />
      <NotesList notes={notes} onEdit={handleEdit} />
    </div>
  );
}
```

### API Client Architecture

```typescript
// lib/api/client.ts - Axios instance with interceptors
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Attempt token refresh
      try {
        const newToken = await refreshAccessToken();
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return axios(error.config);
      } catch {
        // Redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

### Component Patterns

#### Container/Presenter Pattern
```typescript
// Container Component - Business logic
function NotesContainer() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  
  const loadNotes = async () => {
    setLoading(true);
    try {
      const data = await notesApi.getNotes();
      setNotes(data.results);
    } catch (error) {
      handleError(error);
    } finally {
      setLoading(false);
    }
  };
  
  return <NotesList notes={notes} loading={loading} />;
}

// Presenter Component - UI only
function NotesList({ notes, loading }: Props) {
  if (loading) return <LoadingSpinner />;
  return (
    <div>
      {notes.map(note => <NoteCard key={note.id} note={note} />)}
    </div>
  );
}
```

---

## AI Integration

### Gemini Service Implementation

```python
# apps/notes/services/gemini_service.py
class GeminiSummarizer:
    """Service for generating AI summaries using Google Gemini"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.max_retries = settings.GEMINI_MAX_RETRIES
        genai.configure(api_key=self.api_key)
    
    def generate_summary(self, content: str, max_length: int = 150) -> str:
        """
        Generate summary with retry logic and fallback
        
        Args:
            content: Text to summarize
            max_length: Maximum words in summary
            
        Returns:
            Generated summary
            
        Raises:
            AIServiceException: If generation fails after retries
        """
        # Validation
        if not content or len(content.strip()) == 0:
            raise AIServiceException("Cannot summarize empty content")
        
        # Short content handling
        if len(content.split()) <= 20:
            return content[:max_length * 5]
        
        # Retry loop with exponential backoff
        for attempt in range(self.max_retries):
            try:
                prompt = self._build_prompt(content, max_length)
                summary = self._call_gemini_api(prompt)
                return summary
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    # Fallback to extractive summary
                    return self._extractive_summary(content, max_length)
    
    def _build_prompt(self, content: str, max_length: int) -> str:
        """Build optimized prompt for Gemini"""
        return f"""Summarize the following note in approximately {max_length} words or less.
Make it concise, clear, and capture the key points.

Note content:
{content}

Summary:"""
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Make API call to Gemini"""
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'max_output_tokens': 500,
            }
        )
        return response.text.strip()
    
    def _extractive_summary(self, content: str, max_length: int) -> str:
        """Fallback: Extract first sentences as summary"""
        sentences = content.split('. ')
        summary = []
        word_count = 0
        
        for sentence in sentences:
            words = sentence.split()
            if word_count + len(words) <= max_length:
                summary.append(sentence)
                word_count += len(words)
            else:
                break
        
        return '. '.join(summary) + '.'
```

### Prompt Engineering Best Practices

1. **Clear Instructions**
   - Specify exact output format
   - Define length constraints
   - Request specific style

2. **Context Provision**
   - Include relevant metadata
   - Provide examples if needed
   - Set tone and perspective

3. **Error Handling**
   - Validate responses
   - Handle edge cases
   - Implement fallbacks

---

## Database Schema

### Entity-Relationship Diagram

```
┌─────────────────┐         ┌─────────────────┐
│      User       │         │       Tag       │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │─┐   ┌──│ id (PK)         │
│ username        │ │   │  │ name            │
│ email           │ │   │  │ user_id (FK)    │
│ password        │ │   │  │ created_at      │
│ created_at      │ │   │  └─────────────────┘
│ updated_at      │ │   │           │
└─────────────────┘ │   │           │
                    │   │           │
                    ▼   │           │
            ┌─────────────────┐    │
            │      Note       │    │
            ├─────────────────┤    │
            │ id (PK)         │    │
            │ user_id (FK)    │◄───┘
            │ title           │
            │ content         │
            │ summary         │
            │ created_at      │
            │ updated_at      │
            └─────────────────┘
                    │
                    │ Many-to-Many
                    │
            ┌─────────────────┐
            │   Note_Tags     │
            ├─────────────────┤
            │ id (PK)         │
            │ note_id (FK)    │
            │ tag_id (FK)     │
            └─────────────────┘
```

### Database Indexes

```python
# Performance-critical indexes
class Note(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),  # List user notes
            models.Index(fields=['user', 'title']),        # Search by title
        ]

class Tag(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['user', 'name']),  # List user tags
        ]
```

### Migration Strategy

1. **Development**: Create migrations for every model change
2. **Staging**: Test migrations with production-like data
3. **Production**: Run migrations with zero-downtime strategy

```bash
# Generate migration
python manage.py makemigrations

# Review migration SQL
python manage.py sqlmigrate notes 0003

# Apply migration
python manage.py migrate
```

---

## API Design

### RESTful Principles

1. **Resource-Based URLs**
   ```
   GET    /api/notes/          # List resources
   POST   /api/notes/          # Create resource
   GET    /api/notes/:id/      # Retrieve resource
   PUT    /api/notes/:id/      # Update resource
   DELETE /api/notes/:id/      # Delete resource
   ```

2. **HTTP Methods Semantics**
   - GET: Retrieve (idempotent, safe)
   - POST: Create (non-idempotent)
   - PUT/PATCH: Update (idempotent)
   - DELETE: Remove (idempotent)

3. **Status Codes**
   ```
   200 OK                  # Successful GET, PUT, PATCH
   201 Created             # Successful POST
   204 No Content          # Successful DELETE
   400 Bad Request         # Validation error
   401 Unauthorized        # Not authenticated
   403 Forbidden           # Not authorized
   404 Not Found           # Resource doesn't exist
   500 Internal Error      # Server error
   503 Service Unavailable # External service down
   ```

### Pagination Strategy

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Response format:
{
    "count": 100,
    "next": "http://api.example.com/notes/?page=2",
    "previous": null,
    "results": [...]
}
```

### Versioning Strategy

```python
# URL versioning (recommended)
urlpatterns = [
    path('api/v1/', include('apps.notes.urls')),
    path('api/v2/', include('apps.notes.v2_urls')),
]

# Header versioning (alternative)
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
}
```

---

## Security

### Authentication Flow

```
1. User Login
   ↓
2. Server validates credentials
   ↓
3. Server generates JWT tokens
   ├── Access Token (short-lived, 15 min)
   └── Refresh Token (long-lived, 7 days)
   ↓
4. Client stores tokens
   ↓
5. Client includes Access Token in requests
   ↓
6. When Access Token expires:
   ├── Client sends Refresh Token
   ├── Server validates Refresh Token
   ├── Server generates new Access Token
   └── Client updates Access Token
```

### JWT Configuration

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': settings.SECRET_KEY,
}
```

### CORS Configuration

```python
# Development
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# Production
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
]

CORS_ALLOW_CREDENTIALS = True
```

### Input Validation

```python
# Serializer-level validation
class NoteCreateSerializer(serializers.ModelSerializer):
    def validate_title(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Title cannot be empty")
        if len(value) > 200:
            raise serializers.ValidationError("Title too long")
        return value.strip()
    
    def validate_content(self, value):
        # Sanitize HTML if needed
        cleaned_content = bleach.clean(value)
        return cleaned_content
```

### Rate Limiting

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}
```

---

## Testing Strategy

### Backend Testing

#### Unit Tests
```python
# apps/notes/tests/test_models.py
class NoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
    
    def test_create_note(self):
        note = Note.objects.create(
            user=self.user,
            title='Test Note',
            content='Test content'
        )
        self.assertEqual(note.title, 'Test Note')
        self.assertIsNone(note.summary)
    
    def test_note_ordering(self):
        # Notes should be ordered by created_at descending
        note1 = Note.objects.create(user=self.user, title='First')
        note2 = Note.objects.create(user=self.user, title='Second')
        notes = Note.objects.all()
        self.assertEqual(notes[0].title, 'Second')
```

#### Integration Tests
```python
# apps/notes/tests/test_views.py
class NoteViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_notes(self):
        Note.objects.create(user=self.user, title='Note 1', content='Content 1')
        Note.objects.create(user=self.user, title='Note 2', content='Content 2')
        
        response = self.client.get('/api/notes/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_note_with_auto_summarize(self):
        data = {
            'title': 'Test Note',
            'content': 'This is a long note that should be summarized...',
            'auto_summarize': True
        }
        response = self.client.post('/api/notes/', data)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data['summary'])
```

### Frontend Testing

```typescript
// components/notes/NoteCard.test.tsx
describe('NoteCard', () => {
  it('renders note title and content', () => {
    const note: Note = {
      id: 1,
      title: 'Test Note',
      content: 'Test content',
      summary: null,
      tags: [],
      created_at: '2025-01-01',
      updated_at: '2025-01-01',
      user: 'testuser'
    };
    
    render(<NoteCard note={note} />);
    expect(screen.getByText('Test Note')).toBeInTheDocument();
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });
});
```

### Test Coverage Goals

- Unit Tests: > 90%
- Integration Tests: > 80%
- E2E Tests: Critical user flows

---

## Performance Optimization

### Backend Optimization

1. **Database Query Optimization**
   ```python
   # Use select_related for ForeignKey
   notes = Note.objects.select_related('user').all()
   
   # Use prefetch_related for ManyToMany
   notes = Note.objects.prefetch_related('tags').all()
   
   # Avoid N+1 queries
   notes = Note.objects.prefetch_related('tags').filter(user=user)
   for note in notes:
       print(note.tags.all())  # No additional query
   ```

2. **Caching Strategy**
   ```python
   # Cache user tags
   from django.core.cache import cache
   
   def get_user_tags(user_id):
       cache_key = f'user_tags_{user_id}'
       tags = cache.get(cache_key)
       if tags is None:
           tags = Tag.objects.filter(user_id=user_id)
           cache.set(cache_key, tags, 300)  # 5 minutes
       return tags
   ```

3. **Pagination**
   - Always paginate list endpoints
   - Use cursor pagination for large datasets

### Frontend Optimization

1. **Code Splitting**
   ```typescript
   // Lazy load heavy components
   const NoteEditor = dynamic(() => import('@/components/notes/NoteEditor'), {
     loading: () => <LoadingSpinner />,
     ssr: false
   });
   ```

2. **Memoization**
   ```typescript
   const MemoizedNoteCard = React.memo(NoteCard, (prev, next) => {
     return prev.note.id === next.note.id && 
            prev.note.updated_at === next.note.updated_at;
   });
   ```

3. **Debouncing**
   ```typescript
   const debouncedSearch = useMemo(
     () => debounce((query: string) => {
       notesApi.getNotes(query).then(setNotes);
     }, 300),
     []
   );
   ```

---

## Error Handling

### Backend Error Handling

```python
# core/exceptions.py
class AIServiceException(Exception):
    """Exception for AI service errors"""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

# Usage in views
try:
    summary = summarizer.generate_summary(content)
except AIServiceException as e:
    logger.error(f"AI service error: {e.message}")
    return Response(
        {
            'error': 'Summary generation failed',
            'message': e.message,
            'details': e.details
        },
        status=status.HTTP_503_SERVICE_UNAVAILABLE
    )
```

### Frontend Error Handling

```typescript
// lib/utils/errorHandler.ts
export function handleApiError(error: any): string {
  if (error.response) {
    // Server responded with error
    const status = error.response.status;
    const data = error.response.data;
    
    if (status === 400) {
      return data.message || 'Invalid request';
    } else if (status === 401) {
      return 'Please login to continue';
    } else if (status === 503) {
      return 'Service temporarily unavailable';
    }
  } else if (error.request) {
    // Request made but no response
    return 'Network error. Please check your connection.';
  }
  
  return 'An unexpected error occurred';
}
```

---

## Development Workflow

### Git Workflow

```bash
# Feature branch workflow
git checkout -b feature/add-export-functionality
git add .
git commit -m "feat: add note export in multiple formats"
git push origin feature/add-export-functionality
# Create Pull Request
```

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed

### Continuous Integration

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements/dev.txt
          pytest
      - name: Run frontend tests
        run: |
          cd frontend
          npm install
          npm test
```

---

## Conclusion

This technical documentation covers the complete architecture and implementation details of the Smart Notes application. For additional information, refer to:

- API Documentation
- Deployment Guide
- User Manual

**Last Updated**: November 2025
