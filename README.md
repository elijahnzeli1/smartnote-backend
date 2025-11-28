# Smart Notes - AI-Powered Note Taking Application

A full-stack application for creating, managing, and AI-summarizing notes using Django REST Framework backend, React/Next.js frontend, and Google Gemini AI for intelligent summarization.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Features

### Core Functionality
- **User Authentication**: Secure JWT-based authentication with registration and login
- **Note Management**: Full CRUD operations for notes (Create, Read, Update, Delete)
- **AI Summarization**: Automatic note summarization using Google Gemini AI
- **Smart Search**: Search through notes by title or content
- **Tag Organization**: Organize notes with custom tags for easy filtering
- **Export Notes**: Export your notes in JSON, CSV, or Markdown formats

### Advanced Features
- **Auto-Summarization**: Option to automatically generate summaries when creating notes
- **Manual Summarization**: Regenerate summaries on-demand for existing notes
- **Tag Filtering**: Filter notes by specific tags
- **Responsive Design**: Beautiful UI that works seamlessly on all devices
- **Real-time Updates**: Instant feedback on all operations
- **Error Handling**: Comprehensive error handling with user-friendly messages

## 🏗️ Architecture

The application follows clean architecture principles with clear separation of concerns:

### Backend (Django REST Framework)
```
backend/
├── apps/
│   ├── users/          # User authentication & management
│   │   ├── models.py   # Custom User model
│   │   ├── serializers.py
│   │   ├── views.py    # Auth endpoints (register, login, profile)
│   │   └── tests/
│   └── notes/          # Notes & Tags management
│       ├── models.py   # Note and Tag models
│       ├── serializers.py
│       ├── views.py    # CRUD, summarize, export endpoints
│       ├── services/   # Gemini AI integration
│       └── tests/
├── core/               # Shared utilities
│   ├── exceptions.py   # Custom exceptions
│   └── middleware.py   # Custom middleware
└── smartnotes/
    └── settings/       # Split settings (dev/prod)
```

### [Frontend (Next.js + TypeScript)](https://github.com/elijahnzeli1/smartnote-frontend.git)
```
frontend/
└── src/
    ├── app/            # Next.js 14 app router
    │   ├── login/
    │   ├── register/
    │   └── notes/
    ├── components/     # Reusable React components
    │   ├── auth/       # Login & Register forms
    │   ├── notes/      # Note cards, editor, list, tags, export
    │   └── ui/         # Base UI components
    ├── lib/
    │   ├── api/        # API client & methods
    │   └── hooks/      # Custom React hooks
    └── types/          # TypeScript type definitions
```
[Click here to access the frontend](https://github.com/elijahnzeli1/smartnote-frontend.git)
## 📋 Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **PostgreSQL**: 14 or higher (SQLite for development)
- **Google API Key**: For Gemini AI integration

## 🚀 Getting Started

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/dev.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the backend directory:
   ```env
   # Django Configuration
   DJANGO_SECRET_KEY=your-secret-key-here-change-in-production
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database (SQLite for development)
   DATABASE_URL=sqlite:///db.sqlite3
   # For PostgreSQL: postgresql://username:password@localhost:5432/smartnotes_dev
   
   # Google Gemini API
   GOOGLE_API_KEY=your-gemini-api-key-here
   GEMINI_MODEL=gemini-1.5-flash
   GEMINI_MAX_RETRIES=3
   GEMINI_TIMEOUT=30
   
   # CORS (for frontend)
   CORS_ALLOWED_ORIGINS=http://localhost:3000
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   
   Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## 📚 API Documentation

Once the backend is running, you can access:

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`
- **Admin Panel**: `http://localhost:8000/admin/`

### Key Endpoints

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login and get JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET | `/api/auth/profile/` | Get user profile |
| PATCH | `/api/auth/profile/` | Update user profile |

#### Notes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notes/` | List all notes (with search & tag filter) |
| POST | `/api/notes/` | Create new note |
| GET | `/api/notes/{id}/` | Get specific note |
| PUT | `/api/notes/{id}/` | Update note |
| PATCH | `/api/notes/{id}/` | Partial update note |
| DELETE | `/api/notes/{id}/` | Delete note |
| POST | `/api/notes/{id}/summarize/` | Generate AI summary |
| GET | `/api/notes/export/` | Export notes (JSON/CSV/Markdown) |

#### Tags
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tags/` | List all tags |
| POST | `/api/tags/` | Create new tag |
| GET | `/api/tags/{id}/` | Get specific tag |
| PUT | `/api/tags/{id}/` | Update tag |
| DELETE | `/api/tags/{id}/` | Delete tag |

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
pytest
```

With coverage:
```bash
pytest --cov=apps --cov-report=term-missing
```

Run specific test files:
```bash
pytest apps/users/tests/test_auth.py
pytest apps/notes/tests/test_notes.py
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🔧 Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Programming language |
| Django | 5.0 | Web framework |
| Django REST Framework | 3.14+ | REST API framework |
| djangorestframework-simplejwt | 5.3+ | JWT authentication |
| PostgreSQL | 14+ | Production database |
| SQLite | 3 | Development database |
| Google Generative AI | 0.3+ | Gemini AI integration |
| drf-spectacular | 0.26+ | API documentation |
| pytest | 7.4+ | Testing framework |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14 | React framework |
| TypeScript | 5.0+ | Type safety |
| React | 18 | UI library |
| Tailwind CSS | 3.4+ | Styling |
| Axios | 1.6+ | HTTP client |

## 📁 Project Structure

```
SmartNoteAPI/
├── backend/
│   ├── apps/
│   │   ├── notes/          # Notes & Tags app
│   │   │   ├── migrations/
│   │   │   ├── services/   # Gemini AI service
│   │   │   ├── tests/
│   │   │   ├── admin.py
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   └── users/          # User authentication app
│   │       ├── migrations/
│   │       ├── tests/
│   │       ├── admin.py
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── core/               # Shared utilities
│   │   ├── exceptions.py
│   │   └── middleware.py
│   ├── smartnotes/
│   │   ├── settings/       # Split settings
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   └── prod.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── dev.txt
│   │   └── prod.txt
│   ├── manage.py
│   └── pytest.ini
│
├── frontend/
│   └── src/
│       ├── app/            # Next.js pages
│       │   ├── login/
│       │   ├── register/
│       │   ├── notes/
│       │   ├── layout.tsx
│       │   └── page.tsx
│       ├── components/     # React components
│       │   ├── auth/
│       │   │   ├── LoginForm.tsx
│       │   │   └── RegisterForm.tsx
│       │   ├── notes/
│       │   │   ├── NoteCard.tsx
│       │   │   ├── NoteEditor.tsx
│       │   │   ├── NotesList.tsx
│       │   │   ├── TagSelector.tsx
│       │   │   └── ExportButton.tsx
│       │   └── ui/
│       ├── lib/
│       │   └── api/
│       │       ├── auth.ts
│       │       ├── client.ts
│       │       └── notes.ts
│       └── types/
│           └── index.ts
│
├── docs/                   # Additional documentation
├── openapi.yaml           # OpenAPI specification
└── README.md
```

## 🌐 Deployment

### Backend Deployment (Render/Heroku)

1. **Set environment variables**
   ```env
   DJANGO_SECRET_KEY=<your-production-secret-key>
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=your-domain.com
   DATABASE_URL=<your-postgres-url>
   GOOGLE_API_KEY=<your-gemini-api-key>
   CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
   ```

2. **Update settings module**
   ```bash
   export DJANGO_SETTINGS_MODULE=smartnotes.settings.prod
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

### Frontend Deployment (Vercel)

1. **Import repository to Vercel**

2. **Set environment variable**
   ```env
   NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api
   ```

3. **Deploy** - Automatically deploys on push to main branch

## 🔐 Security Best Practices

1. **Never commit sensitive data**
   - Keep `.env` files out of version control
   - Use `.gitignore` to exclude sensitive files

2. **Use environment variables**
   - Store all secrets in environment variables
   - Use different keys for development and production

3. **Enable HTTPS in production**
   - Use SSL/TLS certificates
   - Set `SECURE_SSL_REDIRECT = True` in production

4. **Review CORS settings**
   - Limit `CORS_ALLOWED_ORIGINS` to trusted domains
   - Don't use `CORS_ALLOW_ALL_ORIGINS = True` in production

5. **Keep dependencies updated**
   ```bash
   pip list --outdated
   npm outdated
   ```

## 🎯 Usage Examples

### Create a Note with Tags
```python
# API Request
POST /api/notes/
{
  "title": "Meeting Notes",
  "content": "Discussed project timeline and deliverables...",
  "auto_summarize": true,
  "tag_ids": [1, 2]
}
```

### Search Notes
```python
GET /api/notes/?search=project
```

### Filter by Tag
```python
GET /api/notes/?tag=1
```

### Export Notes
```python
GET /api/notes/export/?format=markdown
GET /api/notes/export/?format=csv&search=important
GET /api/notes/export/?format=json&tag=2
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation as needed
- Keep commits atomic and meaningful

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini** for AI capabilities
- **Django** and **Next.js** communities for excellent frameworks
- All contributors and users of this project

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/SmartNoteAPI/issues)
- **Documentation**: See `/docs` folder for detailed guides
- **Email**: your.email@example.com

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] Voice note transcription
- [ ] Advanced analytics
- [ ] Integration with cloud storage
- [ ] Multi-language support

---

**Made with ❤️ using Django, Next.js, and Google Gemini AI**

*Last updated: November 2025*
