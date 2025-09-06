# Learner Engagement Platform

A comprehensive system designed to identify at-risk learners and provide personalized interventions through automated nudges. The platform combines risk assessment algorithms with AI-powered content generation to improve learner retention and engagement across educational programs.

## Tech Stack

- **Backend**: FastAPI with async SQLAlchemy
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **AI Integration**: OpenAI GPT API with fallback mechanisms
- **Dashboard**: Streamlit for administrative interface
- **Testing**: pytest with async support
- **CI/CD**: GitHub Actions

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Streamlit      │    │  FastAPI        │    │  OpenAI API     │
│  Dashboard      │◄──►│  Backend        │◄──►│  (with fallback)│
│  (Port 8501)    │    │  (Port 8000)    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  SQLite         │
                       │  Database       │
                       └─────────────────┘
```

## Key Features

- **Risk Assessment**: Automated scoring based on engagement metrics
- **AI-Powered Nudges**: Personalized interventions using OpenAI
- **Fallback Mechanisms**: Continues operation when external services fail
- **Real-time Dashboard**: Monitor learners and trigger manual interventions
- **Batch Processing**: Efficient risk score updates for multiple learners
- **RESTful APIs**: Well-structured endpoints for integration

## First-Run Setup

### Prerequisites
- Python 3.10 or 3.11
- pip (Python package manager)
- Git

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd learner-engagement-platform

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install dashboard dependencies
cd dashboard
pip install -r requirements.txt
cd ..
```

### 2. Environment Configuration

```bash
# Copy environment template
copy backend\.env.example backend\.env

# Edit backend/.env with your settings (optional for basic functionality)
# DATABASE_URL=sqlite:///./learner_platform.db
# OPENAI_API_KEY=your_openai_key_here (optional - fallback will be used)
```

### 3. Initialize Database and Seed Data

```bash
# Navigate to backend directory
cd backend

# Run database seed script
python scripts/seed.py

# Verify database creation
dir ..\learner_platform.db
```

### 4. Start Backend Server

```bash
# From backend directory
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Backend will be available at: http://localhost:8000
# API documentation at: http://localhost:8000/docs
```

### 5. Start Dashboard (New Terminal)

```bash
# Activate virtual environment in new terminal
venv\Scripts\activate

# Navigate to dashboard directory
cd dashboard

# Start Streamlit dashboard
streamlit run app.py --server.port 8501

# Dashboard will be available at: http://localhost:8501
```

### 6. Verify Installation

```bash
# Test backend health endpoint
curl http://localhost:8000/api/health

# Expected response: {"status":"ok","time":"2024-XX-XXTXX:XX:XX"}
```

## OpenAI API Key Handling

### With OpenAI API Key
1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Generate an API key
3. Add to `backend/.env`: `OPENAI_API_KEY=your_key_here`
4. Restart backend server

### Without OpenAI API Key (Fallback Mode)
- System automatically uses pre-defined templates from `prompts/fallback_nudges.json`
- All responses include `"gptFallback": true` flag
- Full functionality maintained with simulated AI responses
- Perfect for development and testing

## Demo Script for Hackathon Presentation

### 1. Show Risk Assessment (2 minutes)
```bash
# Open dashboard at http://localhost:8501
# Point out learners sorted by risk level
# Highlight risk scores and labels (high/medium/low)
```

### 2. Generate AI Nudges (3 minutes)
```bash
# Click "Generate Nudge" for high-risk learner
# Show personalized content generation
# Demonstrate fallback behavior (if no API key)
# Try different channels (in-app, WhatsApp, email)
```

### 3. API Integration Demo (2 minutes)
```bash
# Open http://localhost:8000/docs
# Show GET /api/learners endpoint
# Demonstrate POST /api/learners/{id}/nudge
# Show JSON responses with gptFallback flags
```

### 4. Batch Processing (1 minute)
```bash
# Use POST /api/simulate/run endpoint
# Show risk score recalculation for all learners
# Demonstrate auto-nudge generation option
```

### 5. Technical Highlights (2 minutes)
- Async FastAPI for performance
- Robust fallback mechanisms
- SQLAlchemy ORM with proper relationships
- Comprehensive error handling
- Production-ready patterns

## Development Workflow

### Recommended Commit Messages
```bash
git commit -m "feat: add risk scoring algorithm"
git commit -m "fix: handle OpenAI API timeout gracefully"
git commit -m "docs: update API endpoint documentation"
git commit -m "test: add unit tests for nudge generation"
git commit -m "refactor: extract database utilities"
```

### Running Tests
```bash
# From backend directory
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_risk.py -v
```

### Code Quality
```bash
# Format code (if black is installed)
black .

# Lint code (if flake8 is installed)
flake8 .

# Type checking (if mypy is installed)
mypy .
```

### Database Management
```bash
# Reset database (development only)
del ..\learner_platform.db
python scripts/seed.py

# Inspect database
sqlite3 ..\learner_platform.db
.tables
.schema learners
SELECT * FROM learners LIMIT 5;
.quit
```

## API Endpoints

### Core Endpoints
- `GET /api/health` - System health check
- `GET /api/learners` - List all learners with risk filtering
- `GET /api/learners/{id}` - Get individual learner details
- `POST /api/learners/{id}/nudge` - Generate personalized nudge
- `POST /api/learners/{id}/quiz` - Generate quiz content
- `POST /api/simulate/run` - Batch risk recalculation

### Example API Usage
```bash
# Get high-risk learners
curl "http://localhost:8000/api/learners?risk_filter=high"

# Generate nudge for specific learner
curl -X POST "http://localhost:8000/api/learners/aman_sharma/nudge" \
  -H "Content-Type: application/json" \
  -d '{"channel": "in-app"}'
```

## Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check if port 8000 is in use
netstat -an | findstr :8000

# Try different port
uvicorn app:app --reload --port 8001
```

**Dashboard connection error:**
```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Check dashboard API_BASE configuration in dashboard/app.py
```

**Database issues:**
```bash
# Delete and recreate database
del ..\learner_platform.db
python scripts/seed.py
```

**OpenAI API errors:**
- Check API key in `.env` file
- Verify account has credits
- System will automatically fallback to local templates

### Getting Help
1. Check logs in terminal output
2. Verify all dependencies are installed
3. Ensure virtual environment is activated
4. Check that all required files exist in project structure

## Project Structure
```
learner-engagement-platform/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── models.py           # SQLAlchemy models
│   ├── lib_db.py          # Database utilities
│   ├── lib/
│   │   └── risk.py        # Risk scoring algorithm
│   ├── services/
│   │   └── openai_client.py # AI integration
│   ├── routers/
│   │   └── learners.py    # API endpoints
│   ├── scripts/
│   │   └── seed.py        # Database seeding
│   └── tests/
│       └── test_risk.py   # Unit tests
├── dashboard/
│   └── app.py             # Streamlit interface
├── prompts/
│   ├── mock_learners.csv  # Sample data
│   └── fallback_nudges.json # Fallback templates
└── README.md              # This file
```

## Next Steps

1. **Production Deployment**: Configure PostgreSQL, environment variables, and Docker
2. **Enhanced Features**: Add Redis caching, advanced analytics, and notification systems
3. **ML Integration**: Replace heuristic risk scoring with trained models
4. **Mobile Support**: Develop mobile-friendly interfaces
5. **Integration**: Connect with existing LMS platforms

---

Built with ❤️ for improving learner engagement and educational outcomes.