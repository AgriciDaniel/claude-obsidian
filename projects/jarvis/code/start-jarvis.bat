@echo off
REM Jarvis launcher — dubbelklicka denna fil för att starta.
REM Eller skapa en genväg till den på skrivbordet.

cd /d "%~dp0"

echo =========================================
echo   Startar Jarvis...
echo =========================================
echo.

REM Kontrollera att Ollama-service svarar (annars starta den)
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
  echo Ollama-service inte igang. Startar den...
  start "" "%LOCALAPPDATA%\Programs\Ollama\ollama app.exe"
  echo Vantar 5 sekunder pa att den ska komma igang...
  timeout /t 5 /nobreak >nul
)

REM Starta Jarvis
"venv\Scripts\python.exe" jarvis.py

echo.
echo =========================================
echo   Jarvis avslutad.
echo =========================================
pause
