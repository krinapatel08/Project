# HR AI Assistant - Automated Interview System

A full-stack AI-powered HR interview system that automates candidate screening through oral and coding assessments. The system intelligently parses resumes from various sources (PDFs, URLs, Google Sheets) and generates tailored interview questions.

## 🚀 Features

- **Smart Resume Parsing**: Automatically extracts candidate data from PDFs, external links, and Google Sheets
- **AI-Powered Question Generation**: Uses Gemini AI to create job-specific interview questions
- **Multi-Format Support**: Handles PDF uploads, external URLs, and Google Sheets seamlessly
- **Background Processing**: Asynchronous task processing for scalable candidate management
- **Bulk Upload**: CSV-based bulk candidate uploads with automatic processing
- **Interview Management**: Complete workflow from candidate upload to interview completion

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn
- SQLite (included with Python)

## 🛠️ Installation

### Backend Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd AI-Assistant/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
- Windows:
```bash
venv\Scripts\activate
```
- macOS/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure environment variables**
Create a `.env` file in the `backend` directory:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
GEMINI_API_KEY=your-gemini-api-key-optional
FRONTEND_URL=http://localhost:5173
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Seed initial data (optional)**
```bash
python manage.py seed_hr
python manage.py seed_questions
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
Create a `.env` file in the `frontend` directory:
```env
VITE_API_URL=http://localhost:8000/api
```

## 🚀 Running the Application

### Start Backend

Open a terminal in the `backend` directory:

1. **Start Django server**
```bash
python manage.py runserver
```

2. **Start background task worker** (in a new terminal)
```bash
python manage.py process_tasks
```

### Start Frontend

Open a terminal in the `frontend` directory:

```bash
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## 📁 Project Structure

```
AI-Assistant/
├── backend/
│   ├── core/                 # Django project settings
│   ├── hr_system/            # Main application
│   │   ├── models.py         # Database models
│   │   ├── views.py          # API endpoints
│   │   ├── tasks.py          # Background tasks
│   │   ├── serializers.py    # DRF serializers
│   │   └── management/       # Custom commands
│   ├── media/                # Uploaded files
│   ├── db.sqlite3            # SQLite database
│   └── manage.py             # Django CLI
│
└── frontend/
    ├── src/
    │   ├── components/       # React components
    │   ├── pages/            # Page components
    │   └── App.jsx           # Main app component
    ├── package.json          # Node dependencies
    └── vite.config.js        # Vite configuration
```

## 🔑 Key Features Explained

### Resume Parsing Pipeline

1. **Google Sheets Support**: Automatically converts `pubhtml` links to CSV format for reliable data extraction
2. **Dynamic Metadata Extraction**: Uses AI (when available) or smart regex fallback to extract:
   - Full name
   - Email
   - Top 5 skills
   - Years of experience
   - Professional summary
   - Education

3. **Raw Text Storage**: Stores complete resume content for AI question generation

### Bulk Upload Format

CSV files should follow this format:
```csv
Candidate Name,Candidate Email,Resume Link
John Doe,john@example.com,https://example.com/resume.pdf
Jane Smith,jane@example.com,https://docs.google.com/spreadsheets/.../pubhtml
```

Supported column variations:
- Name: `name`, `candidate name`, `Candidate Name`
- Email: `email`, `candidate email`, `Candidate Email`
- Resume: `resume_url`, `resume link`, `Resume Link`, `link`

## 🔧 Configuration

### Gemini API (Optional)

To enable AI-powered features:
1. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add to `.env`: `GEMINI_API_KEY=your-key-here`

Without the API key, the system uses intelligent fallback parsing.

### CORS Settings

Update `backend/core/settings.py` if deploying to a different domain:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://your-production-domain.com",
]
```

## 🐛 Troubleshooting

### Backend Issues

**Database locked error**:
```bash
python manage.py migrate --run-syncdb
```

**Background tasks not processing**:
- Ensure `process_tasks` worker is running
- Check for errors in the terminal output

### Frontend Issues

**Port already in use**:
- Vite will automatically try the next available port (5174, 5175, etc.)

**API connection errors**:
- Verify backend is running on port 8000
- Check CORS settings in `backend/core/settings.py`

## 📝 API Endpoints

### Jobs
- `GET /api/jobs/` - List all jobs
- `POST /api/jobs/` - Create new job
- `GET /api/jobs/{id}/` - Get job details
- `POST /api/jobs/{id}/upload_candidates/` - Upload candidates (CSV or manual)

### Candidates
- `GET /api/candidates/{id}/detail/` - Get candidate details with resume

### Authentication
- `POST /api/auth/login/` - Login (returns token)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini AI for intelligent question generation
- Django & Django REST Framework
- React & Vite
- Background Task library for async processing
