@echo off
REM Add Python Scripts directories to PATH for this session
echo Adding Python Scripts to PATH...

REM Add both system and user Python Scripts directories
set PATH=C:\Python313\Scripts;C:\Users\Sahid\AppData\Roaming\Python\Python313\Scripts;%PATH%

echo PATH updated successfully!
echo.
echo You can now run commands directly:
echo   streamlit run dashboard/app.py
echo   uvicorn backend.app:app
echo.
echo To make this permanent, add these directories to your System Environment Variables:
echo   1. C:\Python313\Scripts
echo   2. C:\Users\Sahid\AppData\Roaming\Python\Python313\Scripts
echo.