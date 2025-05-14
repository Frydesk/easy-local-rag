@echo off
echo Testing Spanish RAG System...

:: Activate virtual environment
call venv\Scripts\activate

:: Check if the API is running
curl -s -f "http://localhost:8000/docs" >nul 2>&1
if errorlevel 1 (
    echo Error: RAG API is not running on port 8000
    echo Please start the API first using start_rag.bat
    pause
    exit /b 1
)

:: Test query
echo.
echo Sending test query...
echo Query: "¿Qué es el Dr. Simi?"
echo.
curl -X POST "http://localhost:8000/query" ^
-H "Content-Type: application/json" ^
-d "{\"text\": \"¿Qué es el Dr. Simi?\"}" ^
-H "Accept: application/json"

echo.
echo.
echo Test complete!
echo If you see a JSON response above, the system is working correctly.
echo If you see an error, please check that:
echo 1. The API is running (start_rag.bat)
echo 2. You have documents in the knowledge folder
echo 3. The documents have been processed (process_knowledge.py)
pause 