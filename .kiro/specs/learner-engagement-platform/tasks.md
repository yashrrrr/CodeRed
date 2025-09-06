# Implementation Plan

- [x] 1. Create project skeleton and packaging structure





  - Initialize directory structure: backend/, dashboard/, prompts/, .git/
  - Create backend/requirements.txt with exact package versions (FastAPI, SQLAlchemy, OpenAI, etc.)
  - Create backend/.env.example with database URL, OpenAI key, and configuration variables
  - Create .gitignore with Python-specific ignores (__pycache__, .venv, *.pyc, .env)
  - Create README_INIT.md with scaffold completion note and next steps
  - _Requirements: 7.2, 7.4_

- [x] 2. Implement FastAPI application core and database models





  - Create backend/app.py with async FastAPI app, startup event for DB table creation, CORS middleware
  - Add health endpoint GET /api/health returning status and timestamp
  - Create backend/models.py with SQLAlchemy ORM models (Learner, Nudge, Event) using async patterns
  - Create backend/lib_db.py with async engine creation and session factory
  - Include router import placeholders and proper type hints throughout
  - _Requirements: 6.1, 6.5, 3.1, 3.3_

- [x] 3. Build risk scoring utility with deterministic algorithm





  - Create backend/lib/risk.py with compute_risk function implementing the exact heuristic formula
  - Add compute_and_update_all function for batch risk processing
  - Implement defensive handling for missing/invalid fields and non-ISO dates
  - Create backend/tests/test_risk.py with pytest tests for low-risk and high-risk scenarios
  - Add comments explaining algorithm and future ML model replacement
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 7.1_

- [x] 4. Implement OpenAI client service with fallback mechanisms





  - Create backend/services/openai_client.py with async generate_nudge and generate_quiz functions
  - Implement OpenAI API integration with httpx.AsyncClient and 8-second timeout
  - Add fallback logic to load prompts/fallback_nudges.json when API key missing or calls fail
  - Include gptFallback flag in all responses and proper error logging without key exposure
  - Add defensive parsing for unexpected API response formats
  - _Requirements: 2.1, 2.2, 2.4, 5.1, 5.3_
-

- [x] 5. Create idempotent database seed script with sample data




  - Create backend/scripts/seed.py with async SQLAlchemy session handling
  - Implement CSV reading from prompts/mock_learners.csv with upsert logic by email
  - Add fallback nudges insertion from prompts/fallback_nudges.json as orphan records
  - Create prompts/mock_learners.csv with 5 sample learner rows (Aman, Riya, Arjun, Sana, Karan)
  - Create prompts/fallback_nudges.json with 3 sample nudge templates
  - Include __main__ block and comprehensive logging for success/failure
  - _Requirements: 3.2, 3.4, 5.5_

- [x] 6. Build REST API endpoints with validation and error handling











  - Create backend/routers/learners.py with APIRouter and all required endpoints
  - Implement GET /api/learners with risk filtering and computed risk scores
  - Add GET /api/learners/{id} returning learner details with nudge history
  - Create POST /api/learners/{id}/nudge with channel validation and OpenAI integration
  - Add POST /api/learners/{id}/quiz calling generate_quiz service
  - Implement POST /api/simulate/run for batch risk recomputation with auto-nudge option
  - Include Pydantic request/response models and proper HTTP status codes
  - Wire router into app.py with include_router
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 2.3, 2.5_

- [x] 7. Create Streamlit dashboard with learner monitoring and manual interventions





  - Create dashboard/app.py with Streamlit interface
  - Implement learner list fetching from backend API with configurable API_BASE
  - Add learner table display showing name, email, completion, risk_label, risk_score
  - Create "Generate Nudge" buttons for each learner with POST request handling
  - Display generated nudges in expandable sections with clear gptFallback indicators
  - Include setup instructions and error handling for backend connectivity
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 8. Add comprehensive testing and CI pipeline










  - Enhance backend/tests/test_risk.py with additional edge cases if needed
  - Create .github/workflows/ci.yml with Python 3.10/3.11 setup
  - Configure pytest execution and optional flake8 linting
  - Set up automated testing on push and pull request events
  - Ensure fast feedback loop for development workflow
  - _Requirements: 7.1, 7.3_
-

- [x] 9. Create comprehensive documentation and developer setup guide




  - Create README.md in repo root with project summary and tech stack overview
  - Add exact first-run checklist with copy-paste commands for environment setup
  - Include backend startup (uvicorn), seed script execution, and dashboard launch
  - Document OpenAI API key handling and fallback behavior
  - Add demo script guidance for hackathon presentation
  - Include recommended commit messages and development workflow
  - _Requirements: 7.2, 7.4, 7.5_

- [x] 10. Document refactoring roadmap and create verification checklist





  - Create REFACTOR.md with prioritized improvement tasks for future iterations
  - Include specific refactors: router splitting, Pydantic schemas, UUID PKs, Alembic migrations
  - Add advanced features: Redis caching, Docker containerization, OpenAI retry logic
  - Create CHECKLIST.md with verification steps for testing and debugging
  - Include fallback testing instructions and database inspection commands
  - Add final commit and deployment preparation steps
  - _Requirements: 7.4, 7.5_