@echo off
echo 🚀 Setting up Learner Engagement Platform Frontend...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo ✅ Node.js version: 
node --version

REM Install dependencies
echo 📦 Installing dependencies...
npm install

REM Create environment file if it doesn't exist
if not exist .env.local (
    echo 📝 Creating environment file...
    copy env.example .env.local
    echo ✅ Created .env.local file. Please review and update if needed.
)

echo.
echo 🎉 Frontend setup complete!
echo.
echo Next steps:
echo 1. Make sure your backend API is running on http://localhost:8000
echo 2. Review .env.local file and update if needed
echo 3. Run 'npm run dev' to start the development server
echo 4. Open http://localhost:3000 in your browser
echo.
echo Happy coding! 🚀
pause
