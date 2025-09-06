# Verification Checklist

This document provides comprehensive verification steps for testing, debugging, and deployment preparation of the Learner Engagement Platform.

## Pre-Deployment Verification

### ✅ Environment Setup Verification

**Backend Environment:**
```bash
# Verify Python version
python --version  # Should be 3.10+

# Check virtual environment
which python  # Should point to venv/Scripts/python (Windows) or venv/bin/python (Unix)

# Verify dependencies
pip list | grep -E "(fastapi|sqlalchemy|openai|uvicorn)"

# Check environment variables
echo $OPENAI_API_KEY  # Should be set or empty (fallback mode)
```

**Dashboard Environment:**
```bash
# Verify Streamlit installation
streamlit --version

# Check dashboard dependencies
pip list | grep -E "(streamlit|requests|pandas)"
```

### ✅ Database Verification

**Database Creation and Seeding:**
```bash
# Start backend to create tables
cd backend
uvicorn app:app --reload &
BACKEND_PID=$!

# Wait for startup
sleep 3

# Verify health endpoint
curl http://localhost:8000/api/health

# Run seed script
python scripts/seed.py

# Stop backend
kill $BACKEND_PID
```

**Database Inspection:**
```bash
# Install sqlite3 if not available
# Windows: Download from https://sqlite.org/download.html
# Linux: sudo apt-get install sqlite3
# macOS: brew install sqlite3

# Inspect database structure
sqlite3 learner_platform.db ".schema"

# Check learner data
sqlite3 learner_platform.db "SELECT COUNT(*) FROM learners;"
sqlite3 learner_platform.db "SELECT name, email, risk_label FROM learners LIMIT 5;"

# Check fallback nudges
sqlite3 learner_platform.db "SELECT COUNT(*) FROM nudges WHERE learner_id IS NULL;"

# Verify risk score distribution
sqlite3 learner_platform.db "SELECT risk_label, COUNT(*) FROM learners GROUP BY risk_label;"
```

### ✅ API Endpoint Testing

**Core API Functionality:**
```bash
# Start backend
cd backend
uvicorn app:app --reload &
BACKEND_PID=$!
sleep 3

# Test health endpoint
curl -X GET http://localhost:8000/api/health

# Test learners list
curl -X GET http://localhost:8000/api/learners

# Test learner details (replace with actual learner ID)
curl -X GET http://localhost:8000/api/learners/learner_001

# Test risk filtering
curl -X GET "http://localhost:8000/api/learners?risk_level=high"

# Test nudge generation (replace with actual learner ID)
curl -X POST http://localhost:8000/api/learners/learner_001/nudge \
  -H "Content-Type: application/json" \
  -d '{"channel": "in-app"}'

# Test quiz generation
curl -X POST http://localhost:8000/api/learners/learner_001/quiz \
  -H "Content-Type: application/json" \
  -d '{}'

# Test simulation run
curl -X POST http://localhost:8000/api/simulate/run \
  -H "Content-Type: application/json" \
  -d '{"auto_nudge": false}'

# Stop backend
kill $BACKEND_PID
```

### ✅ Fallback Mechanism Testing

**OpenAI Fallback Testing:**
```bash
# Test without OpenAI API key
cd backend
unset OPENAI_API_KEY
uvicorn app:app --reload &
BACKEND_PID=$!
sleep 3

# Generate nudge - should use fallback
curl -X POST http://localhost:8000/api/learners/learner_001/nudge \
  -H "Content-Type: application/json" \
  -d '{"channel": "in-app"}' | jq '.gptFallback'
# Should return: true

# Generate quiz - should use fallback
curl -X POST http://localhost:8000/api/learners/learner_001/quiz \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.gptFallback'
# Should return: true

kill $BACKEND_PID
```

**Fallback Content Verification:**
```bash
# Check fallback nudges file exists
ls -la prompts/fallback_nudges.json

# Verify fallback content structure
cat prompts/fallback_nudges.json | jq '.nudges | length'
# Should return: 3 or more

# Check fallback nudge content
cat prompts/fallback_nudges.json | jq '.nudges[0]'
```

### ✅ Dashboard Functionality Testing

**Dashboard Startup and Connectivity:**
```bash
# Start backend first
cd backend
uvicorn app:app --reload &
BACKEND_PID=$!
sleep 3

# Start dashboard in new terminal
cd dashboard
streamlit run app.py &
DASHBOARD_PID=$!
sleep 5

# Verify dashboard is accessible
curl -I http://localhost:8501
# Should return: HTTP/1.1 200 OK

# Stop services
kill $BACKEND_PID $DASHBOARD_PID
```

**Manual Dashboard Testing:**
1. Open http://localhost:8501 in browser
2. Verify learner table loads with data
3. Check risk score colors (red=high, yellow=medium, green=low)
4. Click "Generate Nudge" button for a learner
5. Verify nudge appears in expandable section
6. Check for gptFallback indicator if no OpenAI key
7. Test with different learners to verify functionality

### ✅ Unit Test Execution

**Run Test Suite:**
```bash
cd backend

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_risk.py -v

# Check test results
echo "Exit code: $?"  # Should be 0 for success
```

**Test Coverage Verification:**
```bash
# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux

# Check coverage percentage
python -m pytest tests/ --cov=. --cov-report=term-missing
# Should show coverage for all modules
```

## Debugging and Troubleshooting

### 🔍 Common Issues and Solutions

**Issue: Backend won't start**
```bash
# Check for port conflicts
netstat -an | grep :8000
# If port is in use, kill the process or use different port

# Check Python path and dependencies
which python
pip list | grep fastapi

# Check for syntax errors
python -m py_compile backend/app.py
```

**Issue: Database connection errors**
```bash
# Check database file permissions
ls -la learner_platform.db

# Verify database integrity
sqlite3 learner_platform.db "PRAGMA integrity_check;"

# Check for locked database
lsof learner_platform.db  # Unix/macOS
# Windows: Use Process Explorer to find processes using the file
```

**Issue: OpenAI API failures**
```bash
# Test API key validity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models | jq '.data[0].id'

# Check API quota and usage
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/usage

# Verify fallback mechanism
grep -r "gptFallback" backend/services/
```

**Issue: Dashboard connection errors**
```bash
# Check backend connectivity from dashboard
curl http://localhost:8000/api/health

# Verify API_BASE configuration in dashboard
grep -r "API_BASE" dashboard/

# Check CORS configuration
grep -r "CORSMiddleware" backend/
```

### 🔍 Performance Debugging

**API Response Time Analysis:**
```bash
# Time API calls
time curl -X GET http://localhost:8000/api/learners

# Use httpie for detailed timing
pip install httpie
http --print=HhBb --timeout=30 GET localhost:8000/api/learners

# Monitor with curl timing
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/learners
```

**Database Query Performance:**
```bash
# Enable SQLite query logging (add to app.py temporarily)
# engine = create_async_engine(DATABASE_URL, echo=True)

# Analyze slow queries
sqlite3 learner_platform.db "EXPLAIN QUERY PLAN SELECT * FROM learners WHERE risk_label = 'high';"
```

### 🔍 Log Analysis

**Backend Logs:**
```bash
# Run backend with detailed logging
cd backend
PYTHONPATH=. uvicorn app:app --log-level debug

# Filter specific log types
uvicorn app:app --log-level info 2>&1 | grep -E "(ERROR|WARNING)"

# Save logs to file
uvicorn app:app --log-level info > backend.log 2>&1 &
```

**Dashboard Logs:**
```bash
# Run Streamlit with verbose logging
streamlit run app.py --logger.level debug

# Check Streamlit logs location
ls ~/.streamlit/logs/
```

## Final Deployment Preparation

### 📋 Pre-Commit Checklist

**Code Quality:**
- [ ] All tests pass: `python -m pytest tests/`
- [ ] No linting errors: `flake8 backend/ --max-line-length=100`
- [ ] Code formatted: `black backend/ --check`
- [ ] No security issues: `bandit -r backend/`

**Documentation:**
- [ ] README.md updated with latest setup instructions
- [ ] API documentation generated: `python -c "import app; print(app.app.openapi())"`
- [ ] Environment variables documented in .env.example
- [ ] Deployment guide reviewed and tested

**Configuration:**
- [ ] Production environment variables set
- [ ] Database backup created: `cp learner_platform.db learner_platform.db.backup`
- [ ] Secrets properly configured (not in code)
- [ ] CORS settings appropriate for deployment environment

**Testing:**
- [ ] All API endpoints tested manually
- [ ] Dashboard functionality verified
- [ ] Fallback mechanisms tested
- [ ] Performance acceptable under expected load

### 📋 Deployment Commands

**Final Build and Test:**
```bash
# Clean environment
rm -rf __pycache__ .pytest_cache htmlcov/

# Fresh dependency install
pip install -r backend/requirements.txt
pip install -r dashboard/requirements.txt

# Run full test suite
cd backend && python -m pytest tests/ -v

# Start services for final verification
uvicorn app:app --host 0.0.0.0 --port 8000 &
cd ../dashboard && streamlit run app.py --server.port 8501 &

# Wait and test
sleep 5
curl http://localhost:8000/api/health
curl -I http://localhost:8501

# Stop services
pkill -f uvicorn
pkill -f streamlit
```

**Git Preparation:**
```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "feat: complete learner engagement platform implementation

- Add comprehensive risk scoring algorithm
- Implement OpenAI integration with fallback mechanisms  
- Create Streamlit dashboard for learner monitoring
- Add full test suite and CI pipeline
- Include documentation and deployment guides"

# Tag release
git tag -a v1.0.0 -m "Initial release of Learner Engagement Platform"

# Push to repository
git push origin main --tags
```

### 📋 Production Deployment Checklist

**Infrastructure:**
- [ ] Server/container environment prepared
- [ ] Database configured (SQLite for demo, PostgreSQL for production)
- [ ] Environment variables set securely
- [ ] SSL certificates configured
- [ ] Monitoring and logging set up

**Security:**
- [ ] API keys stored securely (not in code)
- [ ] HTTPS enabled for all endpoints
- [ ] CORS configured for production domains
- [ ] Rate limiting configured
- [ ] Security headers added

**Monitoring:**
- [ ] Health check endpoints accessible
- [ ] Log aggregation configured
- [ ] Error tracking set up (Sentry, etc.)
- [ ] Performance monitoring enabled
- [ ] Backup procedures tested

**Documentation:**
- [ ] Deployment runbook created
- [ ] Rollback procedures documented
- [ ] Monitoring playbook available
- [ ] User guide for dashboard created

## Success Criteria

✅ **All tests pass** - Zero failing unit or integration tests
✅ **API responds correctly** - All endpoints return expected responses
✅ **Dashboard loads** - Streamlit interface displays learner data
✅ **Fallback works** - System functions without OpenAI API key
✅ **Database populated** - Seed data loads successfully
✅ **Documentation complete** - Setup and usage instructions clear
✅ **Performance acceptable** - API responses under 2 seconds
✅ **Error handling robust** - Graceful degradation on failures

## Emergency Rollback

If issues are discovered post-deployment:

```bash
# Quick rollback to previous version
git checkout v0.9.0  # or previous stable tag
docker-compose down && docker-compose up -d

# Database rollback (if needed)
cp learner_platform.db.backup learner_platform.db

# Verify rollback successful
curl http://localhost:8000/api/health
```